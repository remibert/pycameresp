#!/usr/bin/python3
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

# Mov to gif :
# ffmpeg -i video.mov -vf "fps=3,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 output.gif
# 640x360

MICROPYTHON_VERSION ="a1afb337d2629a781cf4e171b7db7f05eeacc78f"
ESP_IDF_VERSION     ="v4.4.1"
ESP32_CAMERA_VERSION="722497cb19383cd4ee6b5d57bb73148b5af41b24" # Stable version but cannot rebuild with chip esp32s3
ESP32_CAMERA_VERSION_S3="1ac48e5397ee22a59a18a314c4acf44c23dfe946" # Reliability problem but Esp32 S3 firmware can build with it

OUTPUT_DIR = os.path.abspath(os.path.normpath(os.environ.setdefault("PYCAMERESP_FIRMWARE",os.path.dirname(__file__)+os.path.sep+"firmware")))

if len(sys.argv) > 1:
	BOARD = sys.argv[1]
else:
	BOARD = "ESP32CAM"
PYCAMERESP_DIR=os.path.abspath(os.path.normpath(os.path.dirname(__file__)))

GET_COMMANDS = """

###################
# Get micropython #
###################
mkdir "%(OUTPUT_DIR)s"
cd "%(OUTPUT_DIR)s"
git clone https://github.com/micropython/micropython.git
cd "%(OUTPUT_DIR)s/micropython"
git checkout %(MICROPYTHON_VERSION)s
cd "%(OUTPUT_DIR)s/micropython/ports/esp32"
git submodule update --init --recursive

#################
# Get espressif #
#################
cd "%(OUTPUT_DIR)s"
git clone -b %(ESP_IDF_VERSION)s --recursive https://github.com/espressif/esp-idf.git

##############
# Get camera #
##############
cd "%(OUTPUT_DIR)s"
git clone https://github.com/espressif/esp32-camera.git esp32-camera
cd "%(OUTPUT_DIR)s/esp32-camera"
git checkout %(ESP32_CAMERA_VERSION)s

cd "%(OUTPUT_DIR)s/esp-idf/components"
ln -s "%(OUTPUT_DIR)s/esp32-camera" esp32-camera"""

BUILD_DOC_COMMANDS= '''

#############
# Build Doc #
#############
cd %(PYCAMERESP_DIR)s/modules/lib
export PYTHONPATH=../simul;pdoc3 --html -o ../../doc --force .
'''

BUILD_COMMANDS = '''

#####################
# Set env espressif #
#####################
cd "%(OUTPUT_DIR)s/esp-idf"
bash install.sh
source ./export.sh

###################
# Build mpy-cross #
###################
cd "%(OUTPUT_DIR)s/micropython"
make -C mpy-cross

#####################
# Build micropython #
#####################
cd "%(OUTPUT_DIR)s/micropython/ports/esp32"
make submodules
make BOARD=%(BOARD)s
cp "%(OUTPUT_DIR)s/micropython/ports/esp32/build-%(BOARD)s/firmware.bin" "%(OUTPUT_DIR)s/%(BOARD)s-firmware.bin"

####################
# Build distri zip #
####################
cd %(PYCAMERESP_DIR)s
python3 "%(PYCAMERESP_DIR)s/scripts/zip_mpy.py" "%(OUTPUT_DIR)s" "%(BOARD)s" "%(PYCAMERESP_DIR)s"
'''

PATCH_COMMANDS = '''

############################
# Patch source Micropython #
############################
cp -f -r -v -p "%(PYCAMERESP_DIR)s/patch/c/micropython/"*       "%(OUTPUT_DIR)s/micropython"
cp -f -r -v -p "%(PYCAMERESP_DIR)s/patch/python/micropython/"*  "%(OUTPUT_DIR)s/micropython"
cp -f -r -v -p "%(PYCAMERESP_DIR)s/modules/lib/"*               "%(OUTPUT_DIR)s/micropython/ports/esp32/modules"
cd %(PYCAMERESP_DIR)s
python3        "%(PYCAMERESP_DIR)s/scripts/patchInisetup.py"    "%(OUTPUT_DIR)s"
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
pip3 install pyqt6
pip3 install pyinstaller
pip3 install esptool
pip3 install --upgrade esptool
pip3 install pyserial
pip3 install requests
pip3 install pdoc3
'''

CLEAN_COMMANDS='''

#######################
# Cleanup all sources #
#######################
cd "%(OUTPUT_DIR)s/micropython"
git fetch --all
git reset --hard 
git clean -fdx

cd "%(OUTPUT_DIR)s/esp32-camera"
git fetch --all
git reset --hard 
git clean -fdx
git checkout %(ESP32_CAMERA_VERSION)s

cd "%(OUTPUT_DIR)s/esp-idf"
git fetch --all
git reset --hard 
git clean -fdx

cd "%(OUTPUT_DIR)s/esp-idf/components"
ln -s "%(OUTPUT_DIR)s/esp32-camera" esp32-camera
'''

# Presence of an old unused camera component version in the firmware, causes a problem to rebuild GENERIC_S3.
# This patch switch to recent version.
S3_PATCH_COMMANDS='''

#############################################
# Replace Camera version for build ESP32 S3 #
#############################################
cd "%(OUTPUT_DIR)s/esp32-camera"
git checkout %(ESP32_CAMERA_VERSION_S3)s
'''

def execute(commands):
	""" Execute shell commands """
	commands = commands%globals()
	for command in commands.split("\n"):
		command = command.strip()
		if len(command) >= 1 and command[0] == "#":
			print("\x1B[38;33m" + command + "\x1B[m")
		elif command.strip() != "":
			print("\x1B[38;32m> " + command + "\x1B[m")
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
						print ("! Remove dir failed '%s'"%directory)
					if os.path.exists(directory):
						time.sleep(1)
			elif cmd[0] == "copyfile":
				shutil.copyfile(cmd[1],cmd[2])
			elif cmd[0] == "copytree" or cmd[0] == "copydir":
				shutil.copytree(cmd[1],cmd[2])
			elif cmd[0] == "remove":
				os.remove(cmd[1])
			elif cmd[0] == "source":
				os.environ["IDF_PATH"] = OUTPUT_DIR + os.sep + "esp-idf"
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
	parser.add_argument("-i", "--install",    help="install the tools required to build the firmware (linux only)", action="store_true")
	parser.add_argument("-g", "--get",        help="get micropython source from git",                               action="store_true")
	parser.add_argument("-d", "--doc",        help="build pycameresp html documentation",                           action="store_true")
	parser.add_argument("-p", "--patch",      help="patch micropython sources with pycameresp patch",               action="store_true")
	parser.add_argument("-b", "--build",      help="build selected firmwares",                                      action="store_true")
	parser.add_argument("-a", "--all",        help="install tools, get source, patch, and build selected firmwares",action="store_true")
	parser.add_argument("-c", "--clean",      help="clean micropython sources to remove all patch",                 action="store_true")
	parser.add_argument("-s", "--s3",         help="build Esp32 S3 without problem",                                action="store_true")
	parser.add_argument("-o", "--outputdir",  help="output directory")
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
			if  not os.path.exists(OUTPUT_DIR + os.sep + "esp32-camera") and \
				not os.path.exists(OUTPUT_DIR + os.sep + "esp-idf") and \
				not os.path.exists(OUTPUT_DIR + os.sep + "micropython"):
				execute(GET_COMMANDS)
			else:
				print("Get sources already done")

		if args.clean or args.s3:
			execute(CLEAN_COMMANDS)

		if args.s3:
			execute(S3_PATCH_COMMANDS)

		if args.doc:
			execute(BUILD_DOC_COMMANDS)

		if args.patch or args.all:
			execute(PATCH_COMMANDS)

		if args.build or args.all:
			board_dir = OUTPUT_DIR + os.path.sep + "micropython/ports/esp32/boards" + os.sep + "*"
			for board in glob.glob(board_dir):
				if os.path.isdir(board):
					board = os.path.split(board)[1]
					for selected_board in args.boards:
						if fnmatch.fnmatch(board, selected_board):
							BOARD = board
							print("\x1B[95m" +"*"*30 + "\x1B[m")
							print("\x1B[95m" +"*"*30 + "\x1B[m")
							print("\x1B[95m" + BOARD + "\x1B[m")
							print("\x1B[95m" +"*"*30 + "\x1B[m")
							print("\x1B[95m" +"*"*30 + "\x1B[m")
							execute(BUILD_COMMANDS)

if __name__ == "__main__":
	main()
