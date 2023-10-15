#!python3.10
# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Build pycameresp firmware """
import sys
import subprocess
import os
import os.path
import glob
import argparse
import fnmatch
import shutil
import time

# In case of error       :
#       [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:997)>
# The solution is to double click on "Install Certificates.command" from python installation.
#
# Mov to gif :
# ffmpeg -i video.mov -vf "fps=3,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 output.gif
# 640x360
#
# Vmware share folder add next lines in /etc/fstab :
# vmhgfs-fuse   /mnt/hgfs    fuse    defaults,allow_other    0    0

# If you have error :
# ModuleNotFoundError: No module named 'click' in Python
# it's due to a bad version of python, usually 3.11, prefer the 3.10

# ESP32 S1
ESP32_CAMERA_S1="esp32-camera-s1"
ESP_IDF_S1     ="esp-idf-s1"
MICROPYTHON_S1 ="micropython-s1"

ESP32_CAMERA_VERSION_S1="722497cb19383cd4ee6b5d57bb73148b5af41b24" # Very stable version but cannot be rebuild with chip esp32s3
ESP_IDF_VERSION_S1     ="7ab8f793ca5b026f37ae812bcc103e3aa698d164" # v4.2.2 Work perfectly with wifi access point on ESP32CAM
ESP_IDF_VERSION_S1     ="d1503315ded139923a1bdd9b280f320c58f90aac" # v4.2.5 Try
ESP_IDF_VERSION_S1     ="e9d442d2b721293497a3a0bcfb45883a7c5111b9" # v4.4 Try
MICROPYTHON_VERSION_S1 ="294baf52b346e400e2255c6c1e82af5b978b18f7" # micropython 1.20

# ESP32 S3
ESP32_CAMERA_S3="esp32-camera-s3"
ESP_IDF_S3     ="esp-idf-s3"
MICROPYTHON_S3 ="micropython-s3"

ESP32_CAMERA_VERSION_S3="d1c9c2cdb3fab523e81e8d953305c00ed54c834c" # After 2.0.5
ESP_IDF_VERSION_S3     ="5181de8ac5ec5e18f04f634da8ce173b7ef5ab73" # 5.0.2
MICROPYTHON_VERSION_S3 ="e00a144008f368df878c12606fdbf651af2a1dc0" # micropython 1.21

if sys.platform == "win32":
	PIP      = "3"
	COLOR_1  = "+"
	COLOR_2  = ""
	COLOR_3  = ""
	NO_COLOR = ""
elif sys.platform == "linux":
	PIP      = "3"
	COLOR_1  = "\x1B[38;33m"
	COLOR_2  = "\x1B[38;32m"
	COLOR_3  = "\x1B[95m"
	NO_COLOR = "\x1B[m"
elif sys.platform == "darwin":
	PIP      = "3.10"
	COLOR_1  = "\x1B[38;33m"
	COLOR_2  = "\x1B[38;32m"
	COLOR_3  = "\x1B[95m"
	NO_COLOR = "\x1B[m"

OUTPUT_DIR =os.path.abspath(os.path.normpath(os.environ.setdefault("PYCAMERESP_FIRMWARE",os.path.abspath(os.path.dirname(__file__))+os.path.sep+"firmware")))

if len(sys.argv) > 1:
	BOARD = sys.argv[1]
else:
	BOARD = "ESP32CAM"
PYCAMERESP_DIR=os.path.abspath(os.path.normpath(os.path.dirname(__file__)))
BOARD_VARIANT = ""
BOARD_VARIANT_FIRMWARE=""



GET_COMMANDS = """
######################
# Get micropython $(MICRO) #
######################
mkdir "%(OUTPUT_DIR)s"

cd "%(OUTPUT_DIR)s"
git clone https://github.com/micropython/micropython.git %(MICROPYTHON_$(MICRO))s

cd "%(OUTPUT_DIR)s/%(MICROPYTHON_$(MICRO))s"
git checkout %(MICROPYTHON_VERSION_$(MICRO))s

cd "%(OUTPUT_DIR)s/%(MICROPYTHON_$(MICRO))s/ports/esp32"
git submodule update --init --recursive

####################
# Get espressif $(MICRO) #
####################
cd "%(OUTPUT_DIR)s"
git clone --recursive https://github.com/espressif/esp-idf.git %(ESP_IDF_$(MICRO))s

cd "%(OUTPUT_DIR)s/%(ESP_IDF_$(MICRO))s"
git checkout %(ESP_IDF_VERSION_$(MICRO))s
git submodule update --init --recursive

#################
# Get camera $(MICRO) #
#################
cd "%(OUTPUT_DIR)s"
git clone https://github.com/espressif/esp32-camera.git %(ESP32_CAMERA_$(MICRO))s

cd %(ESP32_CAMERA_$(MICRO))s
git checkout %(ESP32_CAMERA_VERSION_$(MICRO))s

cd "%(OUTPUT_DIR)s/%(ESP_IDF_$(MICRO))s/components"
ln -s "%(OUTPUT_DIR)s/%(ESP32_CAMERA_$(MICRO))s" esp32-camera

"""


BUILD_DOC_COMMANDS= '''

#############
# Build Doc #
#############
cd %(PYCAMERESP_DIR)s/modules/lib
export PYTHONPATH=../simul;pdoc3 --html -o ../../doc --force .

'''

SET_ESP_COMMANDS='''

########################
# Set env espressif $(MICRO) #
########################
cd "%(OUTPUT_DIR)s/%(ESP_IDF_$(MICRO))s"
bash install.sh
source ./export.sh

'''

BUILD_ESP_COMMANDS = '''

######################
# Build mpy-cross $(MICRO) #
######################
cd "%(OUTPUT_DIR)s/%(MICROPYTHON_$(MICRO))s"
make -C mpy-cross -j 8

########################
# Build micropython $(MICRO) #
########################
cd "%(OUTPUT_DIR)s/%(MICROPYTHON_$(MICRO))s/ports/esp32"
make submodules -j 8
make BOARD=%(BOARD)s %(BOARD_VARIANT)s -j 8
cp "%(OUTPUT_DIR)s/%(MICROPYTHON_$(MICRO))s/ports/esp32/build-%(BOARD)s%(BOARD_VARIANT_FIRMWARE)s/firmware.bin" "%(PYCAMERESP_DIR)s/delivery/%(BOARD)s%(BOARD_VARIANT_FIRMWARE)s-firmware.bin"

'''

BUILD_RP2_COMMANDS = '''

###################
# Build mpy-cross #
###################
cd "%(OUTPUT_DIR)s/%(MICROPYTHON_S1)s""
make -C mpy-cross

########################
# Build %(MICROPYTHON_S1)s" #
########################
cd "%(OUTPUT_DIR)s/%(MICROPYTHON_S1)s/ports/rp2"
make submodules
make BOARD=%(BOARD)s
cp "%(OUTPUT_DIR)s/%(MICROPYTHON_S1)s/ports/rp2/build-%(BOARD)s/firmware.uf2" "%(PYCAMERESP_DIR)s/delivery/%(BOARD)s-firmware.uf2"

'''

ZIP_MODULES = '''

####################
# Build distri zip #
####################
cd %(PYCAMERESP_DIR)s
python3 "%(PYCAMERESP_DIR)s/scripts/zip_mpy.py" "%(OUTPUT_DIR)s" "%(BOARD)s" "$(MICRO)" "%(BOARD_VARIANT_FIRMWARE)s" "%(PYCAMERESP_DIR)s"

'''

PATCH_COMMANDS = '''

###############################
# Patch source %(MICROPYTHON_$(MICRO))s #
###############################
cp -f -r -p "%(PYCAMERESP_DIR)s/patch/$(MICRO)/c/micropython/"*       "%(OUTPUT_DIR)s/%(MICROPYTHON_$(MICRO))s"
cp -f -r -p "%(PYCAMERESP_DIR)s/patch/$(MICRO)/c/esp32-camera/"*      "%(OUTPUT_DIR)s/%(ESP32_CAMERA_$(MICRO))s"
cp -f -r -p "%(PYCAMERESP_DIR)s/patch/$(MICRO)/python/micropython/"*  "%(OUTPUT_DIR)s/%(MICROPYTHON_$(MICRO))s"

cp -f -r -p "%(PYCAMERESP_DIR)s/modules/lib/"*                       "%(OUTPUT_DIR)s/%(MICROPYTHON_$(MICRO))s/ports/esp32/modules"
cp          "%(PYCAMERESP_DIR)s/patch/gitignore/.gitignore"          "%(OUTPUT_DIR)s/%(MICROPYTHON_$(MICRO))s/ports/esp32/modules/.gitignore"
rm -r       "%(OUTPUT_DIR)s/%(MICROPYTHON_$(MICRO))s/ports/esp32/modules/plugins"

cp -f -r -p "%(PYCAMERESP_DIR)s/modules/lib/"*                       "%(OUTPUT_DIR)s/%(MICROPYTHON_$(MICRO))s/ports/rp2/modules"
cp          "%(PYCAMERESP_DIR)s/patch/gitignore/.gitignore"          "%(OUTPUT_DIR)s/%(MICROPYTHON_$(MICRO))s/ports/rp2/modules/.gitignore"
rm -r       "%(OUTPUT_DIR)s/%(MICROPYTHON_$(MICRO))s/ports/rp2/modules/plugins"

cd %(PYCAMERESP_DIR)s
python3        "%(PYCAMERESP_DIR)s/scripts/patchInisetup.py"    "%(OUTPUT_DIR)s/%(MICROPYTHON_$(MICRO))s" "$(MICRO)"

'''

INSTALL_TOOLS_COMMANDS='''

#######################
# Install linux tools #
#######################
sudo apt-get update                  --fix-missing -y
sudo apt-get install git             --fix-missing -y
sudo apt-get install wget            --fix-missing -y
sudo apt-get install make            --fix-missing -y
sudo apt-get install libncurses-dev  --fix-missing -y
sudo apt-get install flex bison      --fix-missing -y
sudo apt-get install gperf           --fix-missing -y
sudo apt-get install scite           --fix-missing -y
sudo apt-get install python3-pip     --fix-missing -y
sudo apt-get install python3-tk      --fix-missing -y
sudo apt-get install python3-venv    --fix-missing -y
sudo apt-get install cmake           --fix-missing -y

############################
# Install python libraries #
############################
pip%(PIP)s install pyqt6
pip%(PIP)s install pyinstaller
pip%(PIP)s install esptool
pip%(PIP)s install --upgrade esptool
pip%(PIP)s install pyserial
pip%(PIP)s install requests
pip%(PIP)s install pdoc3

'''

CLEAN_COMMANDS='''

##########################
# Cleanup %(MICROPYTHON_$(MICRO))s #
##########################

cd "%(OUTPUT_DIR)s/%(MICROPYTHON_$(MICRO))s"
git clean -fdx
git fetch --all
git reset --hard 

git checkout %(MICROPYTHON_VERSION_$(MICRO))s

cd "%(OUTPUT_DIR)s/%(MICROPYTHON_$(MICRO))s/ports/esp32"
git submodule update --init --recursive

######################
# Cleanup %(ESP_IDF_$(MICRO))s #
######################

cd "%(OUTPUT_DIR)s/%(ESP_IDF_$(MICRO))s"
git clean -fdx
git fetch --all
git reset --hard %(ESP_IDF_VERSION_$(MICRO))s
git checkout %(ESP_IDF_VERSION_$(MICRO))s
git submodule update --init --recursive

###########################
# Cleanup %(ESP32_CAMERA_$(MICRO))s #
###########################

cd "%(OUTPUT_DIR)s/%(ESP32_CAMERA_$(MICRO))s"
git clean -fdx
git fetch --all
git reset --hard %(ESP32_CAMERA_VERSION_$(MICRO))s
git checkout %(ESP32_CAMERA_VERSION_$(MICRO))s

cd "%(OUTPUT_DIR)s/%(ESP_IDF_$(MICRO))s/components"
ln -s "%(OUTPUT_DIR)s/%(ESP32_CAMERA_$(MICRO))s" esp32-camera

'''

PURGE_CSS='''
#############
# Purge CSS #
#############

purgecss --css modules/www/bootstrap.min.css.ref --content modules/www/*.html modules/www/*.js -o modules/www/bootstrap.min.css
'''

# Presence of an old unused camera component version in the firmware, causes a problem to rebuild GENERIC_S3.
# This patch switch to recent version.

def execute(commands, s3=False):
	""" Execute shell commands """
	commands = commands.replace("$(MICRO)","S3" if s3 else "S1")
	commands = commands%globals()
	for command in commands.split("\n"):
		command = command.strip()
		if len(command) >= 1 and command[0] == "#":
			print(COLOR_1 + command + NO_COLOR)
		elif command.strip() != "":
			print(COLOR_2 + "> " + command + NO_COLOR)
			command = command.replace("\t"," ")
			cmds = command.split(" ")
			cmd = []
			for part in cmds:
				if len(part) > 0:
					cmd.append(part)
			if cmd[0] == "cd":
				command = command.strip()
				current_dir = command[3:].strip()
				if current_dir[0] == '"' and current_dir[-1] == '"':
					current_dir = current_dir.strip('"')
				os.chdir(current_dir)
			elif cmd[0] == "removetree" or cmd[0] == "removedir":
				directory = cmd[1]
				while os.path.exists(directory):
					try:
						shutil.rmtree(directory,0,lambda function,directory,dummy: (os.chmod(directory, 0o777),os.remove(directory)))
					except OSError:
						print("! Remove dir failed '%s'"%directory)
					if os.path.exists(directory):
						time.sleep(1)
			elif cmd[0] == "copyfile":
				shutil.copyfile(cmd[1],cmd[2])
			elif cmd[0] == "copytree" or cmd[0] == "copydir":
				shutil.copytree(cmd[1],cmd[2])
			elif cmd[0] == "remove":
				os.remove(cmd[1])
			elif cmd[0] == "source":
				if s3:
					os.environ["IDF_PATH"] = OUTPUT_DIR + os.sep + ESP_IDF_S3
				else:
					os.environ["IDF_PATH"] = OUTPUT_DIR + os.sep + ESP_IDF_S1
				pipe = subprocess.Popen(""". ./export.sh; env""", stdout=subprocess.PIPE, shell=True)
				lines = pipe.communicate()[0]
				for line in lines.split(b"\n"):
					try:
						key, value = line.split(b"=")
						os.environ[key.decode("utf8")] = value.decode("utf8")
					except:
						pass
			else:
				pipe = subprocess.Popen(command, stdout=sys.stdout, stderr=sys.stderr, shell=True)
				lines = pipe.communicate()[0]
		else:
			print("")

def main():
	""" Build pycameresp firmwares """
	global OUTPUT_DIR
	global BOARD
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--install",      help="install the tools required to build the firmware (linux only)", action="store_true")
	parser.add_argument("-g", "--get",          help="get micropython source from git",                               action="store_true")
	parser.add_argument("-d", "--doc",          help="build pycameresp html documentation",                           action="store_true")
	parser.add_argument("-p", "--patch",        help="patch micropython sources with pycameresp patch",               action="store_true")
	parser.add_argument("-b", "--build",        help="build selected firmwares",                                      action="store_true")
	parser.add_argument("-a", "--all",          help="install tools, get source, patch, and build selected firmwares",action="store_true")
	parser.add_argument("-c", "--clean",        help="clean micropython sources to remove all patch",                 action="store_true")
	parser.add_argument("-s", "--s3",           help="build Esp32 S3 without problem",                                action="store_true")
	parser.add_argument("-v", "--boardvariant", help="build with board variant option",                               type=str)
	parser.add_argument("-r", "--rp2",          help="build raspberry pico RP2 and RP2 W",                            action="store_true")
	parser.add_argument("-z", "--zippy",        help="zip python modules",                                            action="store_true")
	parser.add_argument("-u", "--purgecss",     help="purge css content",                                             action="store_true")
	parser.add_argument("-o", "--outputdir",    help="output directory")
	parser.add_argument('boards',  metavar='boards', type=str, help='Select boards to build micropython firmwares, for all firmwares use "*"', nargs="*")
	args = parser.parse_args()
	if len(args.boards) == 0:
		parser.print_help()
	else:
		if args.outputdir is not None:
			OUTPUT_DIR = os.path.abspath(os.path.normpath(args.outputdir))

		if (args.install or args.all) and sys.platform == "linux":
			execute(INSTALL_TOOLS_COMMANDS)

		if (args.get or args.all):
			if not args.s3 and \
				(not os.path.exists(OUTPUT_DIR + os.sep + ESP32_CAMERA_S1) or \
				 not os.path.exists(OUTPUT_DIR + os.sep + ESP_IDF_S1) or \
				 not os.path.exists(OUTPUT_DIR + os.sep + MICROPYTHON_S1)):
				execute(GET_COMMANDS, args.s3)
			elif args.s3 and \
				(not os.path.exists(OUTPUT_DIR + os.sep + ESP32_CAMERA_S3) or \
				 not os.path.exists(OUTPUT_DIR + os.sep + ESP_IDF_S3) or \
				 not os.path.exists(OUTPUT_DIR + os.sep + MICROPYTHON_S3)):
				execute(GET_COMMANDS, args.s3)
			else:
				print("Get sources already done")

		if args.clean or args.all:
			execute(CLEAN_COMMANDS, args.s3)
		
		if args.boardvariant:
			global BOARD_VARIANT
			global BOARD_VARIANT_FIRMWARE
			BOARD_VARIANT = "BOARD_VARIANT=%s"%args.boardvariant
			BOARD_VARIANT_FIRMWARE = "-%s"%args.boardvariant

		if args.doc:
			execute(BUILD_DOC_COMMANDS)

		if args.purgecss or args.patch or args.all:
			execute(PURGE_CSS)

		if args.patch or args.all:
			execute(PATCH_COMMANDS, args.s3)

		if args.zippy:
			execute(ZIP_MODULES, args.s3)

		if args.build or args.all:
			if args.rp2:
				board_dir = OUTPUT_DIR + os.path.sep + "micropython-$(MICRO)/ports/rp2/boards" + os.sep + "*"
			else:
				board_dir = OUTPUT_DIR + os.path.sep + "micropython-$(MICRO)/ports/esp32/boards" + os.sep + "*"
			board_dir = board_dir.replace("$(MICRO)","s3" if args.s3 else "s1")
			for board in glob.glob(board_dir):
				if os.path.isdir(board):
					board = os.path.split(board)[1]
					for selected_board in args.boards:
						if fnmatch.fnmatch(board, selected_board):
							BOARD = board
							print(COLOR_3 +"*"*30 + NO_COLOR)
							print(COLOR_3 +"*"*30 + NO_COLOR)
							print(COLOR_3 + BOARD + NO_COLOR)
							print(COLOR_3 +"*"*30 + NO_COLOR)
							print(COLOR_3 +"*"*30 + NO_COLOR)
							if args.rp2:
								execute(BUILD_RP2_COMMANDS)
							else:
								execute(SET_ESP_COMMANDS, args.s3)
								print("IDF_PATH='%s'"%os.environ["IDF_PATH"])
								execute(BUILD_ESP_COMMANDS, args.s3)
							execute(ZIP_MODULES, args.s3)

if __name__ == "__main__":
	import sys
	if sys.version_info.major == 3 and sys.version_info.minor >= 11:
		print("For the moment only python 3.10 work well")
	else:
		main()
		pass

	print(sys.version_info)
