# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
# pylint:disable=too-many-lines
# pylint:disable=consider-using-f-string
# pylint:disable=unspecified-encoding
""" Class defining a minimalist shell, directly executable on the board.
We modify directories, list, delete, move files, edit files ..
The commands are :
- cd          : change directory
- pwd         : current directory
- cat         : display the content of file
- cls         : clear screen
- mkdir       : create directory
- mv          : move file
- rmdir       : remove directory
- cp          : copy file
- rm          : remove file
- ls          : list file
- ll          : list file long
- date        : get the system date or synchronize with Ntp
- setdate     : set date and time
- uptime      : the amount of time system is running
- find        : find a file
- run         : execute python script
- download    : transfer files from device to computer (only available with camflasher)
- upload      : transfer files from computer to device (only available with camflasher)
- edit        : edit a text file
- exit        : exit of shell
- gc          : garbage collection
- grep        : grep text in many files
- mount       : mount sd card
- umount      : umount sd card
- temperature : device temperature
- meminfo     : memory informations
- flashinfo   : flash informations
- sysinfo     : system informations
- deepsleep   : deepsleep of board
- ping        : ping host
- reboot      : reboot board
- help        : list all command available
- man         : manual of one command
- df          : display free disk space
- ip2host     : convert ip address in hostname
- host2ip     : convert hostname in ip address
- eval        : evaluation python string
- exec        : execute python string
- dump        : display hexadecimal dump of the content of file
"""
# pylint:disable=wrong-import-position
import sys
import io
import os
import uos
import machine
import tools.useful
import tools.logger
import tools.sdcard
import tools.filesystem
import tools.exchange
import tools.info
import tools.strings
import tools.terminal
import tools.watchdog
import tools.lang
import tools.date
import tools.console
import tools.system
import tools.archiver

shell_commands = None

def get_screen_size():
	""" Return the screen size and check if output redirected """
	# pylint:disable=global-variable-not-assigned
	if tools.console.Console.is_redirected() is False:
		height, width = tools.terminal.get_screen_size()
	else:
		height, width = tools.terminal.MAXINT, 80
	return height, width

def cd(directory = "/"):
	""" Change directory """
	try:
		uos.chdir(tools.filesystem.normpath(directory))
	except:
		if directory != ".":
			tools.console.Console.print("No such file or directory '%s'"%directory)

def pwd():
	""" Display the current directory """
	tools.console.Console.print("%s"%uos.getcwd())

def mkdir(directory, recursive=False, quiet=False):
	""" Make directory """
	try:
		if quiet is False:
			tools.console.Console.print("mkdir '%s'"%directory)
		tools.filesystem.makedir(tools.filesystem.normpath(directory), recursive)
	except:
		tools.console.Console.print("Cannot mkdir '%s'"%directory)

def removedir(directory, force=False, quiet=False, simulate=False, ignore_error=False):
	""" Remove directory """
	try:
		if tools.filesystem.exists(directory+"/.DS_Store"):
			rmfile(directory+"/.DS_Store", quiet, force, simulate)
		if (tools.filesystem.ismicropython() or force) and simulate is False:
			uos.rmdir(directory)
		if quiet is False:
			tools.console.Console.print("rmdir '%s'"%(directory))
	except:
		if ignore_error is False:
			tools.console.Console.print("rmdir '%s' not removed"%(directory))

def rmdir(directory, recursive=False, force=False, quiet=False, simulate=False, ignore_error=False):
	""" Remove directory """
	directory = tools.filesystem.normpath(directory)
	if recursive is False:
		removedir(directory, force=force, quiet=quiet, simulate=simulate, ignore_error=ignore_error)
	else:
		directories = [directory]
		d = directory
		while 1:
			parts = tools.filesystem.split(d)
			if parts[1] == "" or parts[0] == "":
				break
			directories.append(parts[0])
			d = parts[0]
		if "/" in directories:
			directories.remove("/")
		if tools.sdcard.SdCard.get_mountpoint() in directories:
			directories.remove(tools.sdcard.SdCard.get_mountpoint())
		for d in directories:
			if tools.filesystem.exists(d) and d != ".":
				removedir(d, force=force, quiet=quiet, simulate=simulate, ignore_error=ignore_error)

def mv(source, destination):
	""" Move or rename file """
	try:
		uos.rename(tools.filesystem.normpath(source),tools.filesystem.normpath(destination))
	except:
		tools.console.Console.print("Cannot mv '%s'->'%s'"%(source,destination))

def copyfile(src,dst,quiet):
	""" Copy file """
	dst = dst.replace("//","/")
	dst = dst.replace("//","/")
	dstdir, dstfile = tools.filesystem.split(dst)
	try:
		if not tools.filesystem.exists(dstdir):
			if dstdir != "." and dstdir != "":
				mkdir(dstdir, recursive=True, quiet=quiet)
		src_file = open(src, 'rb')
		dst_file = open(dst, 'wb')
		if quiet is False:
			tools.console.Console.print("cp '%s' -> '%s'"%(src,dst))
		while True:
			buf = src_file.read(256)
			if len(buf) > 0:
				dst_file.write(buf)
			if len(buf) < 256:
				break
		src_file.close()
		dst_file.close()
	except:
		tools.console.Console.print("Cannot cp '%s' -> '%s'"%(src, dst))

def cp(source, destination, recursive=False, quiet=False):
	""" Copy file command """
	source = tools.filesystem.normpath(source)
	destination = tools.filesystem.normpath(destination)
	if tools.filesystem.isfile(source):
		copyfile(source,destination,quiet)
	else:
		if tools.filesystem.isdir(source):
			path = source
			pattern = "*"
		else:
			path, pattern = tools.filesystem.split(source)

		_, filenames = tools.filesystem.scandir(path, pattern, recursive)

		for src in filenames:
			dst = destination + "/" + src[len(path):]
			copyfile(src,dst,quiet)

def rmfile(filename, quiet=False, force=False, simulate=False):
	""" Remove file """
	try:
		if (tools.filesystem.ismicropython() or force) and simulate is False:
			uos.remove(tools.filesystem.normpath(filename))
		if quiet is False:
			tools.console.Console.print("rm '%s'"%(filename))
	except:
		tools.console.Console.print("rm '%s' not removed"%(filename))

def rm(file, recursive=False, quiet=False, force=False, simulate=False):
	""" Remove file command """
	file = tools.filesystem.normpath(file)
	filenames   = []
	directories = []

	if tools.filesystem.isfile(file):
		path = file
		rmfile(file, force=force, quiet=quiet, simulate=simulate)
	else:
		if tools.filesystem.isdir(file):
			if recursive:
				directories.append(file)
				path = file
				pattern = "*"
			else:
				path = None
				pattern = None
		else:
			path, pattern = tools.filesystem.split(file)

		if path is None:
			tools.console.Console.print("Cannot rm '%s'"%file)
		else:
			dirs, filenames = tools.filesystem.scandir(path, pattern, recursive)
			directories += dirs

			for filename in filenames:
				rmfile(filename, force=force, quiet=quiet, simulate=simulate)

			if recursive:
				directories.sort()
				directories.reverse()

				for directory in directories:
					rmdir(directory, recursive=recursive, force=force, quiet=quiet, simulate=simulate, ignore_error=True)

class LsDisplayer:
	""" Ls displayer class """
	def __init__(self, path, showdir, long):
		""" Constructor """
		self.height, self.width = get_screen_size()
		self.count = 1
		self.long = long
		self.path = path
		self.showdir = showdir

	def purge_path(self, path):
		""" Purge the path for the display """
		path = path.encode("utf8")
		path = tools.filesystem.normpath(path)
		prefix = tools.filesystem.prefix([path, self.path.encode("utf8")])
		return path[len(prefix):].lstrip(b"/")

	def show(self, path):
		""" Show the information of a file or directory """
		fileinfo = tools.filesystem.fileinfo(path)
		file_date = fileinfo[8]
		size = fileinfo[6]

		# If directory
		if fileinfo[0] & 0x4000 == 0x4000:
			if self.showdir:
				if self.long:
					message = b"%s %s [%s]"%(tools.date.date_to_bytes(file_date),b" "*7,self.purge_path(path))
				else:
					message = b"[%s]"%self.purge_path(path)
				self.count = print_part(message, self.width, self.height, self.count)
		else:
			if self.long:
				fileinfo = tools.filesystem.fileinfo(path)
				file_date = fileinfo[8]
				size = fileinfo[6]
				message = b"%s %s %s"%(tools.date.date_to_bytes(file_date),tools.strings.size_to_bytes(size),self.purge_path(path))
			else:
				message = self.purge_path(path)
			self.count = print_part(message, self.width, self.height, self.count)

	def show_dir(self, state):
		""" Indicates if the directory must show """
		self.showdir = state

def ls(file="", recursive=False, long=False):
	""" List files command """
	searchfile(file, recursive, LsDisplayer(uos.getcwd(), True, long))

def ll(file="", recursive=False):
	""" List files long command """
	searchfile(file, recursive, LsDisplayer(uos.getcwd(), True, True))

def searchfile(file, recursive, obj = None):
	""" Search file """
	file = tools.filesystem.normpath(file)
	p = tools.filesystem.abspath(uos.getcwd(), file)
	filenames = []
	try:
		if file == "":
			_,filenames = tools.filesystem.scandir(uos.getcwd(), "*", recursive, obj)
		elif tools.filesystem.isfile(p):
			if obj is not None:
				obj.show_dir(False)
				obj.show(p)
			filenames = [p]
		elif tools.filesystem.isdir(p):
			_, filenames = tools.filesystem.scandir(p, "*", recursive, obj)
		else:
			path, pattern = tools.filesystem.split(p)
			if obj is not None:
				obj.show_dir(False)
			_, filenames = tools.filesystem.scandir(path, pattern, recursive, obj)
	except Exception as err:
		tools.console.Console.print(err)
	if len(filenames) == 0 and file != "" and file != ".":
		tools.console.Console.print("%s : No such file or directory"%file)
	return filenames

def find(file):
	""" Find a file in directories """
	filenames = searchfile(file, True)
	for filename in filenames:
		tools.console.Console.print(filename)

def print_part(message, width, height, count):
	""" Print a part of text """
	# pylint:disable=global-variable-not-assigned
	if isinstance(message , bytes):
		message = message.decode("utf8")
	if count is not None and count >= height:
		tools.console.Console.print(message,end="")
		if tools.console.Console.is_redirected() is False:
			key = tools.terminal.getch()
		else:
			key = " "
		count = 1
		if key in ["x","X","q","Q","\x1B"]:
			return None
		tools.console.Console.print("\n", end="")
	else:
		if count is None:
			count = 1
		else:
			count += 1
		tools.console.Console.print(message)
	return count

def grep(file, text, recursive=False, ignorecase=False, regexp=False):
	""" Grep command """
	from re import search
	file = tools.filesystem.normpath(file)
	def __search(text, content, ignorecase, regexp):
		if ignorecase:
			content  = content.lower()
			text = text.lower()
		if regexp:
			if search(text, content):
				return True
		else:
			if content.find(text) != -1:
				return True
		return False

	def __grep(text, filename, ignorecase, regexp, width, height, count):
		lineNumber = 1
		with open(filename,"r", encoding="latin-1") as f:
			while 1:
				line = f.readline()
				if line:
					if __search(text, line, ignorecase, regexp):
						line = line.replace("\t","    ")
						message = "%s:%d:%s"%(filename, lineNumber, line)
						message = message.rstrip()[:width]
						count = print_part(message, width, height, count)
						if count is None:
							tools.console.Console.print("")
							return None
					lineNumber += 1
				else:
					break
		return count

	if tools.filesystem.isfile(file):
		filenames = [file]
	else:
		path, pattern = tools.filesystem.split(file)
		_, filenames = tools.filesystem.scandir(path, pattern, recursive)

	height, width = get_screen_size()
	count = 1
	for filename in filenames:
		count = __grep(text, filename, ignorecase, regexp, width, height, count)
		if count is None:
			break

def ping(host):
	""" Ping host """
	try:
		from server.ping import ping as ping_
		ping_(host, count=4, timeout=1)
	except:
		tools.console.Console.print("Not available")

def ip2host(ip_address):
	""" Convert ip to hostname """
	try:
		import wifi.station
		_, _, _, dns = wifi.station.Station.get_info()
		from server.dnsclient import resolve_hostname
		tools.console.Console.print(resolve_hostname(dns, ip_address))
	except:
		tools.console.Console.print("Not available")

def host2ip(hostname):
	""" Convert hostname to ip """
	try:
		import wifi.station
		_, _, _, dns = wifi.station.Station.get_info()
		from server.dnsclient import resolve_ip_address
		tools.console.Console.print(resolve_ip_address(dns, hostname))
	except:
		tools.console.Console.print("Not available")

def mountsd(mountpoint="/sd"):
	""" Mount command """
	try:
		tools.sdcard.SdCard.mount(mountpoint)
		tools.console.Console.print("Sd mounted on '%s'"%mountpoint)
	except:
		tools.console.Console.print("Cannot mount sd on '%s'"%mountpoint)

def umountsd(mountpoint="/sd"):
	""" Umount command """
	try:
		tools.sdcard.SdCard.umount(mountpoint)
		tools.console.Console.print("Sd umounted from '%s'"%mountpoint)
	except:
		tools.console.Console.print("Cannot umount sd from '%s'"%mountpoint)

def date_time(update=False, offsetUTC=+1, noDst=False):
	""" Get or set date """
	try:
		from server.timesetting import set_date
		if update:
			if noDst:
				dst = False
			else:
				dst = True
			set_date(offsetUTC, dst)
		del sys.modules["server.timesetting"]
	except:
		pass
	tools.console.Console.print(tools.date.date_to_string())

def setdate(datetime=""):
	""" Set date and time """
	import re
	file_date=re.compile("[/: ]")
	failed = False
	try:
		spls = file_date.split(datetime)

		lst = []
		if len(spls) > 1:
			for spl in spls:
				if len(spl) > 0:
					try:
						r = spl.lstrip("0")
						if len(r) == 0:
							lst.append(0)
						else:
							lst.append(eval(r))
					except:
						failed = True
						break
			if len(lst) == 6:
				# pylint: disable=unbalanced-tuple-unpacking
				year,month,day,hour,minute,second = lst
				machine.RTC().datetime((year, month, day, 0, hour, minute, second, 0))
			else:
				failed = True
		else:
			failed = True
	except Exception as err:
		failed = True
		tools.logger.syslog(err)

	if failed is True:
		tools.console.Console.print('Expected format "YYYY/MM/DD hh:mm:ss"')

def formatsd(fstype="FAT"):
	""" Format sd card """
	if fstype in ["FAT","LFS"]:
		if tools.sdcard.SdCard.is_mounted() is False:
			res = input("All data will be lost on Sd card ? proceed with format (y/n) :")
			if res in ["y","Y"]:
				if tools.sdcard.SdCard.formatsd() is True:
					tools.console.Console.print("Formatting terminated")
				else:
					tools.console.Console.print("Formatting failed")
		else:
			tools.console.Console.print("Sd card is mounted, a reboot required")
	else:
		tools.console.Console.print("Filesystem supported : FAT or LFS")

def reboot():
	""" Reboot command """
	try:
		tools.system.reboot("Reboot device with command")
	except:
		machine.deepsleep(1000)

def deepsleep(seconds=60):
	""" Deep sleep command """
	machine.deepsleep(int(seconds)*1000)

def ligthsleep(seconds=60):
	""" Light sleep command """
	machine.lightsleep(int(seconds)*1000)

edit_class = None
def edit(file, no_color=False, read_only=False):
	""" Edit command """
	# pylint:disable=global-variable-not-assigned
	global edit_class
	if tools.console.Console.is_redirected() is False:
		if edit_class is None:
			try:
				from shell.editor import Editor
			except:
				from editor import Editor
			edit_class = Editor
		edit_class(file, no_color=no_color, read_only=read_only)

def cat(file):
	""" Cat command """
	try:
		f = open(file, "r")
		height, width = get_screen_size()
		count = 1
		while 1:
			line = f.readline()
			if not line:
				break
			message = line.replace("\t","    ").rstrip()[:width]
			count = print_part(message, width, height, count)
			if count is None:
				break
		f.close()
	except:
		tools.console.Console.print("Cannot cat '%s'"%(file))

def df(mountpoint = None):
	""" Display free disk space """
	tools.console.Console.print(tools.strings.tostrings(tools.info.flashinfo(mountpoint=mountpoint)))

def gc():
	""" Garbage collector command """
	from gc import collect
	collect()

def uptime():
	""" Tell how long the system has been running """
	tools.console.Console.print(tools.strings.tostrings(tools.info.uptime()))

def man(command):
	""" Man command """
	tools.console.Console.print(man_one(command))

def man_one(command_name):
	""" Manual of one command """
	try:
		command_name, command_function, command_params, command_flags = get_command(command_name)
		text = "  " + command_name + " "
		for param in command_params:
			text += param + " "
		text += "\n"
		for flag,flagName,val in command_flags:
			text += "    %s : %s\n"%(flag,flagName)
		result = text[:-1]
	except:
		result = "Unknown command '%s'"%command_name
	return result

# pylint: disable=redefined-builtin
def help():
	""" Help command """
	height, width = get_screen_size()
	count = 1
	cmds = list(shell_commands.keys())
	cmds.sort()
	for command in cmds:
		lines = man_one(command)
		lines = "-"*30+"\n" + lines
		for line in lines.split("\n"):
			count = print_part(line, width, height, count)
			if count is None:
				return

def eval_(string):
	""" Evaluate content of string """
	tools.console.Console.print(eval(string))

def exec_(string):
	""" Execute content of string """
	exec(string)

shell_exited = False
def exit():
	""" Exit shell command """
	global shell_exited
	shell_exited = True

def dump_(filename):
	""" dump file content """
	height, width = get_screen_size()
	if tools.console.Console.is_redirected() is False:
		width = (width - 12)//4
	else:
		width = 16
	offset = 0
	file = open(filename, "rb")
	data = b' '
	count = 1
	while True:
		line = io.BytesIO()
		line.write(b'%08X  ' % offset)
		data = file.read(width)
		if len(data) <= 0:
			break
		tools.strings.dump_line (data, line, width)
		offset += width
		count = print_part(line.getvalue(), width, height, count)
		if count is None:
			break

def cls():
	""" clear screen """
	tools.console.Console.print("\x1B[2J\x1B[0;0f", end="")

def check_cam_flasher():
	""" Check if the terminal is CamFlasher """
	# pylint:disable=global-variable-not-assigned
	if tools.console.Console.is_redirected() is False:
		# Request terminal device attribut
		sys.stdout.write(b"\x1B[0c")

		# Wait terminal device attribut response
		response = tools.terminal.getch(duration=1000)

		# If CamFlasher detected
		if response == "\x1B[?3;2c":
			return True
	return False

def upload(file="", recursive=False):
	""" Upload file from computer to device """
	if check_cam_flasher():
		tools.console.Console.print("Upload to device start")
		try:
			command = tools.exchange.UploadCommand(uos.getcwd())
			command.write(file, recursive, sys.stdin.buffer, sys.stdout.buffer)
			result = True
			while result:
				file_reader = tools.exchange.FileReader()
				result = file_reader.read(uos.getcwd(), sys.stdin.buffer, sys.stdout.buffer)
				tools.watchdog.WatchDog.feed()
			tools.console.Console.print("Upload end")
		except Exception as err:
			tools.logger.syslog(err, display=False)
			tools.console.Console.print("Upload failed")
	else:
		tools.console.Console.print("CamFlasher application required for this command")

class Exporter:
	""" Exporter file to camflasher """
	def __init__(self):
		""" Constructor """

	def send_file(self, path):
		""" Send the file """
		result = True
		fileinfo = tools.filesystem.fileinfo(path)

		# If a file
		if fileinfo[0] & 0x4000 != 0x4000:
			file_write = tools.exchange.FileWriter()
			if tools.filesystem.exists(path):
				sys.stdout.buffer.write("࿊".encode("utf8"))
				result = file_write.write(path, sys.stdin.buffer, sys.stdout.buffer)
				tools.watchdog.WatchDog.feed()
		return result

	def show(self, path):
		""" Show the information of a file or directory """
		for _ in range(3):
			# If the send successful exit, else retry three time
			if self.send_file(path) is True:
				break

	def show_dir(self, state):
		""" Indicates if the directory must show """

def download(file="", recursive=False):
	""" Download file from device to computer """
	if check_cam_flasher():
		tools.console.Console.print("Download from device start")
		try:
			searchfile(file, recursive, Exporter())
			tools.console.Console.print ("Download end")
		except Exception as err:
			tools.logger.syslog(err, display=False)
			tools.console.Console.print("Download failed")
	else:
		tools.console.Console.print("CamFlasher application required for this command")

def temperature():
	""" Get the internal temperature """
	celcius, farenheit = tools.info.temperature()
	tools.console.Console.print("%.2f°C, %d°F"%(celcius, farenheit))

def meminfo():
	""" Get memory informations """
	tools.console.Console.print(tools.strings.tostrings(b"%s : %s"%(tools.lang.memory_label, tools.info.meminfo())))

def flashinfo(mountpoint=None):
	""" Get flash informations """
	tools.console.Console.print(tools.strings.tostrings(b"%s : %s"%(tools.lang.flash_label, tools.info.flashinfo(mountpoint=mountpoint))))

def sysinfo():
	""" Get system informations """
	tools.console.Console.print(tools.strings.tostrings(tools.info.sysinfo()))

def vtcolors():
	""" Show all VT100 colors """
	res = b'\x1B[4m4 bits colors\x1B[m\n'
	for i in range(16):
		if i % 8 == 0:
			res += b"\n  "
		if i < 9:
			forecolor = 15
		else:
			forecolor = 0
		res += b"\x1B[38;5;%dm\x1B[48;5;%dm %2d \x1B[0m"%(forecolor, i,i)
	res += b'\n\n\x1B[4m8 bits colors\x1B[m\n'
	j = 0
	for i in range(16,256):
		if j % 12== 0:
			res += b"\n  "
		backcolor = i
		if j % 36 < 36//2:
			forecolor = 15
		else:
			forecolor = 0
		res += b"\x1B[38;5;%dm\x1B[48;5;%dm %3d \x1B[0m"%(forecolor,backcolor,i)
		j += 1
	res += b'\n\n\x1B[4mModifiers\x1B[m\n\n'

	for i,j in [(0,"reset/normal"),(1,b"bold"),(3,b"italic"),(4,b"underline"),(7,b"reverse")]:
		res += b"  %d : \x1B[%dm%s\x1B[0m\n"%(i,i,j)
	res += b'\n\x1B[4mExamples\x1B[m\n\n'
	res += b'  >>> print("\\033[\033[1m1\033[m;\033[7m7\033[mmBold reverse\\033[0m")\n'
	res += b"  \033[1;7mBold reverse\033[0m"
	res += b"\n\n"
	res += b'  >>> print("\033[38;5;15m\033[48;5;1m\\033[48;5;1m\033[m\033[38;5;13m\\033[38;5;13m\033[mHello\\033[m")\n'
	res += b"  \033[48;5;1m\033[38;5;13mHello\033[m\n"

	tools.console.Console.print(res.decode("utf8"))

def get_command(command_name):
	""" Get a command callback according to the command name """
	try:
		# pylint:disable=global-variable-not-assigned
		global shell_commands
		command = shell_commands[command_name]
		command_function = command[0]
		command_params = []
		command_flags  = []
		for item in command[1:]:
			if type(item) == type(""):
				command_params.append(item)
			if type(item) == type((0,)):
				command_flags.append(item)
	except  Exception as err:
		# pylint: disable=raise-missing-from
		raise RuntimeError("Command not found '%s'"%command_name)
	return command_name, command_function, command_params, command_flags

def exec_command(args):
	""" Execute command """
	# pylint:disable=global-variable-not-assigned
	command_name = ""
	command_function = None
	command_params = []
	command_flags = []
	output_redirection = None
	output_filename = None
	try:
		if len(args) >= 1:
			paramsCount = 0
			flags   = {}
			for arg in args:
				arg = arg.strip()
				if len(arg) > 0:
					if command_name == "":
						command_name, command_function, command_params, command_flags = get_command(arg)
					else:
						if len(arg) >= 2 and arg[:2] == "--":
							for commandFlag in command_flags:
								if arg.strip()[2:] == commandFlag[1].strip():
									flags[commandFlag[1]] = commandFlag[2]
									break
							else:
								raise RuntimeError("Illegal option '%s'"%arg)
						elif arg[0] == "-":
							for commandFlag in command_flags:
								if arg.strip() == commandFlag[0].strip():
									flags[commandFlag[1]] = commandFlag[2]
									break
							else:
								raise RuntimeError("Illegal option '%s'"%arg)
						elif arg[0] == ">":
							output_redirection = True
						else:
							if output_redirection is None:
								if paramsCount >= len(command_params):
									raise RuntimeError("Too many parameters on '%s'"%command_name)
								else:
									flags[command_params[paramsCount]] = arg
									paramsCount += 1
							elif output_redirection is True:
								output_filename = arg

	except Exception as err:
		tools.console.Console.print(err)
		return
	tools.console.Console.close()
	try:
		if command_name.strip() != "":
			if output_filename is not None:
				try:
					tools.console.Console.open(output_filename)
				except:
					pass
			command_function(**flags)
	except TypeError as err:
		tools.logger.syslog(err, display=False)
		tools.console.Console.print("Missing parameters for '%s'"%command_name)
	except KeyboardInterrupt as err:
		tools.logger.syslog(err)
		tools.console.Console.print(" [Canceled]")
	except Exception as err:
		tools.logger.syslog(err)
	finally:
		tools.console.Console.close()

def parse_command_line(commandLine):
	""" Parse command line """
	commands_ = []
	args = []
	quote = None
	arg = ""
	for char in commandLine:
		if char == '"' or char == "'":
			if quote is not None:
				if quote == char:
					args.append(arg)
					arg = ""
					quote = None
				else:
					arg += char
			else:
				quote = char
		elif char == " ":
			if quote is not None:
				arg += char
			else:
				args.append(arg)
				arg = ""
		elif char == ";":
			if quote is not None:
				arg += char
			else:
				if len(arg) > 0:
					args.append(arg)
				commands_.append(args)
				arg = ""
				args = []
		else:
			arg += char
	if len(arg) > 0:
		args.append(arg)
	if len(args) > 0:
		commands_.append(args)

	for command in commands_:
		exec_command(command)

def commands(path=None, throw=False):
	""" Start the shell """
	global shell_exited, shell_commands
	current_dir = uos.getcwd()

	create_shell_commands()

	if path is not None:
		uos.chdir(path)

	shell_exited = False
	while shell_exited is False:
		try:
			commandLine = ""
			commandLine = input("%s=> "%os.getcwd())
			tools.watchdog.WatchDog.feed()
		except EOFError:
			tools.console.Console.print("")
			break
		except KeyboardInterrupt:
			tools.console.Console.print("Ctr-C detected, use 'exit' to restart server or 'quit' to get python prompt")

		if commandLine.strip() == "quit":
			if throw is True:
				raise KeyboardInterrupt()
			else:
				break
		parse_command_line(commandLine)

	shell_commands = None
	uos.chdir(current_dir)

def create_shell_commands():
	""" Return the shell commands """
	global shell_commands
	shell_commands = \
	{
		"cd"         :[cd              ,"directory"            ],
		"pwd"        :[pwd                                     ],
		"cat"        :[cat             ,"file"                 ],
		"cls"        :[cls                                     ],
		"mkdir"      :[mkdir           ,"directory",             ("-r","recursive",True)],
		"mv"         :[mv              ,"source","destination" ],
		"rmdir"      :[rmdir           ,"directory",             ("-r","recursive",True),("-f","force",True),("-q","quiet",True),("-s","simulate",True)],
		"cp"         :[cp              ,"source","destination",  ("-r","recursive",True),("-q","quiet",True)],
		"rm"         :[rm              ,"file",                  ("-r","recursive",True),("-f","force",True),("-s","simulate",True)],
		"ls"         :[ls              ,"file",                  ("-r","recursive",True),("-l","long",True)],
		"ll"         :[ll              ,"file",                  ("-r","recursive",True)],
		"date"       :[date_time       ,"offsetUTC" ,            ("-u","update",True),   ("-n","noDst",True)],
		"setdate"    :[setdate         ,"datetime"             ],
		"uptime"     :[uptime                                  ],
		"find"       :[find            ,"file"                 ],
		"run"        :[tools.useful.run      ,"filename"             ],
		"download"   :[download        ,"file",                  ("-r","recursive",True)],
		"upload"     :[upload          ,"file",                  ("-r","recursive",True)],
		"edit"       :[edit            ,"file",                  ("-n","no_color",True),("-r","read_only",True)],
		"exit"       :[exit                                    ],
		"gc"         :[gc                                      ],
		"grep"       :[grep            ,"text","file",           ("-r","recursive",True),("-i","ignorecase",True),("-e","regexp",True)],
		"mount"      :[mountsd         ,"mountpoint"           ],
		"umount"     :[umountsd        ,"mountpoint"           ],
		"temperature":[temperature                             ],
		"meminfo"    :[meminfo                                 ],
		"flashinfo"  :[flashinfo                               ],
		"sysinfo"    :[sysinfo                                 ],
		"deepsleep"  :[deepsleep       ,"seconds"              ],
		"lightsleep" :[ligthsleep      ,"seconds"              ],
		"ping"       :[ping            ,"host"                 ],
		"reboot"     :[reboot                                  ],
		"help"       :[help                                    ],
		"man"        :[man             ,"command"              ],
		"memdump"    :[tools.info.memdump                            ],
		"df"         :[df              ,"mountpoint"           ],
		"ip2host"    :[ip2host         ,"ip_address"           ],
		"host2ip"    :[host2ip         ,"hostname"             ],
		"eval"       :[eval_           ,"string"               ],
		"exec"       :[exec_           ,"string"               ],
		"dump"       :[dump_           ,"filename"             ],
		"formatsd"   :[formatsd        ,"fstype"               ],
		"vtcolors"   :[vtcolors                                ],
	}

if __name__ == "__main__":
	commands(sys.argv[1])
