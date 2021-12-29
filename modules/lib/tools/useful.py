# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Miscellaneous utility functions """
import sys
import os
import io
import time
import select
try:
	import machine
except:
	pass
try:
	from tools import fnmatch
except:
	import fnmatch
try:
	import uos
except:
	pass
# pylint:disable=ungrouped-imports
# pylint:disable=consider-using-enumerate
from tools.tasking import WatchDog

def ismicropython():
	""" Indicates if the python is micropython """
	if sys.implementation.name == "micropython":
		return True
	return False

if ismicropython():
	def get_length_utf8(key):
		""" Get the length utf8 string """
		if len(key) > 0:
			char = key[0]
			if char <= 0x7F:
				return 1
			elif char >= 0xC2 and char <= 0xDF:
				return 2
			elif char >= 0xE0 and char <= 0xEF:
				return 3
			elif char >= 0xF0 and char <= 0xF4:
				return 4
			return 1
		else:
			return 0

	def is_key_ended(key):
		""" Indicates if the key completly entered """
		if len(key) == 0:
			return False
		else:
			char = key[-1]
			if len(key) == 1:
				if char == 0x1B:
					return False
				elif get_length_utf8(key) == len(key):
					return True
			elif len(key) == 2:
				if key[0] == b"\x1B" and key[1] == b"\x1B":
					return False
				elif key[0] == b"\x1B":
					if  key[1] == b"[" or key[1] == b"(" or \
						key[1] == b")" or key[1] == b"#" or \
						key[1] == b"?" or key[1] == b"O":
						return False
					else:
						return True
				elif get_length_utf8(key) == len(key):
					return True
			else:
				if key[-1] >= ord("A") and key[-1] <= ord("Z"):
					return True
				elif key[-1] >= ord("a") and key[-1] <= ord("z"):
					return True
				elif key[-1] == b"~":
					return True
				elif key[0] != b"\x1B" and get_length_utf8(key) == len(key):
					return True
		return False

	def getch(raw = True, duration=100000000, interchar=0.05):
		""" Wait a key pressed on keyboard and return it """
		key = b""
		WatchDog.feed()
		while 1:
			if len(key) == 0:
				delay = duration
			else:
				delay = interchar
			keyPressed = kbhit(delay)
			if is_key_ended(key):
				break
			if keyPressed:
				key += sys.stdin.buffer.read(1)
			else:
				if len(key) > 0:
					break
		try:
			key = key.decode("utf8")
		except:
			key = dump(key,withColor=False)
		return key

	def kbhit(duration=0.01):
		""" Indicates if a key is pressed or not """
		r,w,e = select.select([sys.stdin],[],[],duration)
		if r != []:
			return True
		return False

	def kbflush(duration=0.1):
		""" Flush all keys not yet read """
		while 1:
			r,w,e = select.select([sys.stdin],[],[],duration)
			if r != []:
				sys.stdin.buffer.read(1)
			else:
				break
else:
	def getch(raw = True, duration=100000000, interchar=0.01):
		""" Wait a key pressed on keyboard and return it """
		return read_keyboard(duration, raw, get_char)

	def kbhit(duration=0.001):
		""" Indicates if a key is pressed or not """
		return read_keyboard(duration, True, test_char)

	def get_char(stdins):
		""" Get character """
		if stdins != []:
			return stdins[0].read()
		return None

	def test_char(stdins):
		""" Test a character """
		if stdins != []:
			return True
		return False

	def read_keyboard(duration=0.001, raw=True, callback=None):
		""" Read keyboard on os/x, linux or windows"""
		import tty
		import termios
		import fcntl
		fd = sys.stdin.fileno()
		oldattr = termios.tcgetattr(fd)
		oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
		try:
			newattr = oldattr[:]
			newattr[3] = newattr[3] & ~termios.ICANON
			newattr[3] = newattr[3] & ~termios.ECHO
			termios.tcsetattr(fd, termios.TCSANOW, newattr)

			fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

			if raw:
				tty.setraw(fd)
			key = None
			try:
				inp, outp, err = select.select([sys.stdin], [], [], duration)
			except Exception as err:
				syslog(err)
			result = callback(inp)
		finally:
			# Reset the terminal:
			fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
			termios.tcsetattr(fd, termios.TCSAFLUSH, oldattr)
		return result

	def kbflush(duration=0.5):
		""" Flush all keys not yet read """

try:
	# pylint: disable=no-name-in-module

	from time import ticks_ms
	def ticks():
		""" Count tick elapsed from start """
		return ticks_ms()
except:
	def ticks():
		""" Count tick elapsed from start """
		return (int)(time.time() * 1000)

def ticks_to_string():
	""" Create a string with tick in seconds """
	tick = ticks()
	return "%d.%03d s"%(tick/1000, tick%1000)

previousTime = 0
def log(msg):
	""" Log line with a ticks displayed """
	current = ticks()
	global previousTime
	if previousTime == 0:
		previousTime = current
	if msg is not None:
		print("%03d.%03d:%s"%((current-previousTime)/1000, (current-previousTime)%1000, msg))
	previousTime = ticks()

def date_to_string(date = None):
	""" Get a string with the current date """
	return date_to_bytes(date).decode("utf8")

def date_to_bytes(date = None):
	""" Get a bytes with the current date """
	year,month,day,hour,minute,second,weekday,yearday = time.localtime(date)[:8]
	return b"%04d/%02d/%02d  %02d:%02d:%02d"%(year,month,day,hour,minute,second)

def date_ms_to_string():
	""" Get a string with the current date with ms """
	ms = (time.time_ns() // 1000000)%1000
	year,month,day,hour,minute,second,weekday,yearday = time.localtime(None)[:8]
	return "%04d/%02d/%02d %02d:%02d:%02d.%03d"%(year,month,day,hour,minute,second,ms)

def date_to_filename(date = None):
	""" Get a filename with a date """
	filename = date_to_string(date)
	filename = filename.replace("  "," ")
	filename = filename.replace(" ","_")
	filename = filename.replace("/","-")
	filename = filename.replace(":","-")
	return filename

def date_to_path(date=None):
	""" Get a path with year/month/day/hour """
	year,month,day,hour,minute,second,weekday,yearday = time.localtime(date)[:8]
	return b"%04d/%02d/%02d/%02dh%02d"%(year,month,day,hour,minute)

def size_to_string(size, largeur=6):
	""" Convert a size in a string with k, m, g, t..."""
	return size_to_bytes(size, largeur).decode("utf8")

def size_to_bytes(size, largeur=6):
	""" Convert a size in a bytes with k, m, g, t..."""
	if size > 1073741824*1024:
		return  b"%*.2fT"%(largeur, size / (1073741824.*1024.))
	elif size > 1073741824:
		return  b"%*.2fG"%(largeur, size / 1073741824.)
	elif size > 1048576:
		return b"%*.2fM"%(largeur, size / 1048576.)
	elif size > 1024:
		return b"%*.2fK"%(largeur, size / 1024.)
	else:
		return b"%*dB"%(largeur, size)

def meminfo(display=True):
	""" Get memory informations """
	import gc
	try:
		# pylint: disable=no-member
		alloc = gc.mem_alloc()
		free  = gc.mem_free()
		result = b"Mem alloc=%s free=%s total=%s"%(size_to_bytes(alloc, 1), size_to_bytes(free, 1), size_to_bytes(alloc+free, 1))
		if display:
			print(tostrings(result))
		else:
			return result
	except:
		return b"Mem unavailable"

def flashinfo(display=True):
	""" Get flash informations """
	try:
		import esp
		result = b"Flash user=%s size=%s"%(size_to_bytes(esp.flash_user_start(), 1), size_to_bytes(esp.flash_size(), 1))
		if display:
			print(tostrings(result))
		else:
			return result
	except:
		return b"Flash unavailable"

def sysinfo(display=True, text=""):
	""" Get system informations """
	try:
		result = b"%s%s %dMhz, %s, %s, %s"%(text, sys.platform, machine.freq()//1000000, date_to_bytes(), meminfo(False), flashinfo(False))
		if display:
			print(tostrings(result))
		else:
			return result
	except:
		return b"Sysinfo not available"

def splitext(p):
	""" Split file extension """
	sep='\\'
	altsep = '/'
	extsep = '.'
	sepIndex = p.rfind(sep)
	if altsep:
		altsepIndex = p.rfind(altsep)
		sepIndex = max(sepIndex, altsepIndex)

	dotIndex = p.rfind(extsep)
	if dotIndex > sepIndex:
		filenameIndex = sepIndex + 1
		while filenameIndex < dotIndex:
			if p[filenameIndex:filenameIndex+1] != extsep:
				return p[:dotIndex], p[dotIndex:]
			filenameIndex += 1
	return p, p[:0]

def split(p):
	""" Split file """
	sep = "/"
	i = p.rfind(sep) + 1
	head, tail = p[:i], p[i:]
	if head and head != sep*len(head):
		head = head.rstrip(sep)
	return head, tail

def import_(filename):
	""" Import filename """
	path, file = split(filename)
	moduleName, ext = splitext(file)

	if path not in sys.path:
		sys.path.append(path)

	try:
		del sys.modules[moduleName]
	except:
		pass
	try:
		exec("import %s"%moduleName)

		for fct in dir(sys.modules[moduleName]):
			if fct == "main":
				print("Start main function")
				sys.modules[moduleName].main()
				break
	except Exception as err:
		syslog(err)
	except KeyboardInterrupt as err:
		syslog(err)

def temperature():
	""" Get the internal temperature in celcius and farenheit """
	try:
		import esp32
		farenheit = esp32.raw_temperature()
		celcius = (farenheit-32)/1.8
		return (celcius, farenheit)
	except:
		return (0,0)

def abspath(cwd, payload):
	""" Get the absolute path """
	# Just a few special cases "..", "." and ""
	# If payload start's with /, set cwd to /
	# and consider the remainder a relative path
	if payload.startswith('/'):
		cwd = "/"
	for token in payload.split("/"):
		if token == '..':
			if cwd != '/':
				cwd = '/'.join(cwd.split('/')[:-1])
				if cwd == '':
					cwd = '/'
		elif token != '.' and token != '':
			if cwd == '/':
				cwd += token
			else:
				cwd = cwd + '/' + token
	return cwd

def abspathbytes(cwd, payload):
	""" Get the absolute path into a bytes """
	# Just a few special cases "..", "." and ""
	# If payload start's with /, set cwd to /
	# and consider the remainder a relative path
	if payload.startswith(b'/'):
		cwd = b"/"
	for token in payload.split(b"/"):
		if token == b'..':
			if cwd != b'/':
				cwd = b'/'.join(cwd.split(b'/')[:-1])
				if cwd == b'':
					cwd = b'/'
		elif token != b'.' and token != b'':
			if cwd == b'/':
				cwd += token
			else:
				cwd = cwd + b'/' + token
	return cwd

def exists(filename):
	""" Test if the filename existing """
	try:
		rstat = os.lstat(filename)
		return True
	except:
		try:
			rstat = os.stat(filename)
			return True
		except:
			pass
	return False

previousFileInfo = []
def fileinfo(path):
	""" Get the file informations """
	global previousFileInfo
	if len(previousFileInfo) == 0:
		previousFileInfo = [path, os.stat(path)]
	elif previousFileInfo[0] != path:
		previousFileInfo = [path, os.stat(path)]
	return previousFileInfo[1]

def isdir(path):
	""" Indicates if the path is a directory """
	try:
		if fileinfo(path)[0] & 0x4000 == 0x4000:
			return True
	except:
		pass
	return False

def isfile(path):
	""" Indicates if the path is a file """
	try:
		if fileinfo(path)[0] & 0x4000 == 0:
			return True
	except:
		pass
	return False

def filesize(path):
	""" Get the file size """
	info = fileinfo(path)
	return info[6]

def filetime(path):
	""" Get the file modified time """
	return fileinfo(path)[8]

def exception(err, msg=""):
	""" Return the content of exception into a string """
	file = io.StringIO()
	if ismicropython():
		# pylint: disable=no-member
		sys.print_exception(err, file)
		text = file.getvalue()
	else:
		try:
			import traceback
			file.write(traceback.format_exc())
		except Exception as err:
			print(err)
		text = file.getvalue()
	return text

def syslog(err, msg="", display=True):
	""" Log the error in syslog.log file """
	filename = "syslog.log"
	if isinstance(err, Exception):
		err = exception(err)
	if ismicropython():
		filename = "/" + filename
	if msg != "":
		msg += "\n"
		if display:
			print(tostrings(msg))
	if display:
		print(tostrings(err))

	logFile = open(filename,"a")
	logFile.seek(0,2)

	if logFile.tell() >32*1024:
		logFile.close()
		print("File %s too big"%filename)
		rename(filename + ".3",filename + ".4")
		rename(filename + ".2",filename + ".3")
		rename(filename + ".1",filename + ".2")
		rename(filename       ,filename + ".1")
		logFile = open(filename,"a")

	result = "%s%s"%(tostrings(msg),tostrings(err))
	logFile.write(date_ms_to_string() + " %s\n"%(result))
	logFile.close()
	return result

def html_exception(err):
	""" Return the content of exception into an html bytes """
	text = exception(err)
	text = text.replace("\n    ","<br>&nbsp;&nbsp;&nbsp;&nbsp;")
	text = text.replace("\n  ","<br>&nbsp;&nbsp;")
	text = text.replace("\n","<br>")
	return tobytes(text)

def blink(duration=10):
	""" Blink led """
	try:
		# pylint: disable=no-name-in-module
		from time import sleep_ms
		pin2 = machine.Pin(2, machine.Pin.OUT)
		pin2.value(1)
		sleep_ms(duration)
		pin2.value(0)
		sleep_ms(duration)
	except:
		print("Blink")

screenSize = None

def refresh_screen_size():
	""" Refresh the screen size """
	global screenSize
	try:
		sys.stdout.write("\x1B"+"7")      # Save cursor position
		sys.stdout.write("\x1B[999;999f") # Set cursor position far
		sys.stdout.write("\x1B[6n")       # Cursor position report
		try:
			sys.stdout.flush()
		except:
			pass

		size = getch(raw=False, duration=1, interchar=0.2)
		size = size[2:-1].split(";")
		screenSize = int(size[0]), int(size[1])
		if screenSize[0] < 5 or screenSize[1] < 5:
			result = screenSize
			screenSize = None
		else:
			result = screenSize
	except:
		screenSize = None
		result = (18,40)

	sys.stdout.write("\x1B"+"8") # Restore cursor position
	kbflush()
	return result

def get_screen_size():
	""" Get the VT100 screen size """
	global screenSize
	if screenSize is not None:
		return screenSize
	else:
		return refresh_screen_size()

def prefix(files):
	""" Get the common prefix of all files """
	# Initializes counters
	counters = []

	# For all files
	for file in files:
		# Split the file name into a piece
		paths = file.split("/")

		# For each piece
		for i in range(0,len(paths)):
			try:
				try:
					# Test if counters exist
					counters[i][paths[i]] += 1
				except:
					# Creates a path counters
					counters[i][paths[i]] = 1
			except:
				# Adds a new level of depth
				counters.append({paths[i] : 1})

	# Constructs the prefix of the list of files
	try:
		result = ""
		amount = list(counters[0].values())[0]
		for counter in counters:
			if len(counter.keys()) == 1 and list(counter.values())[0] == amount:
				result += list(counter.keys())[0] + "/"
			else:
				return result [:-1]
		return result
	except IndexError:
		return ""

def now():
	""" Get time now """
	return time.localtime()

def compute_hash(string):
	""" Compute hash
	>>> print(compute_hash("1234"))
	49307
	>>> print(compute_hash(b"1234"))
	49307
	"""
	string = tostrings(string)
	hash_ = 63689
	for char in string:
		hash_ = hash_ * 378551 + ord(char)
	return hash_ % 65536

def isascii(char):
	""" Indicates if the char is ascii """
	if len(char) == 1:
		if ord(char) >= 0x20 and ord(char) != 0x7F or char == "\t":
			return True
	return False

def isupper(char):
	""" Indicates if the char is upper """
	if len(char) == 1:
		if ord(char) >= 0x41 and ord(char) <= 0x5A:
			return True
	return False

def islower(char):
	""" Indicates if the char is lower """
	if len(char) == 1:
		if ord(char) >= 0x61 and ord(char) < 0x7A:
			return True
	return False

def isdigit(char):
	""" Indicates if the char is a digit """
	if len(char) == 1:
		if ord(char) >= 0x31 and ord(char) <= 0x39:
			return True
		return False

def isalpha(char):
	""" Indicates if the char is alpha """
	return isupper(char) or islower(char) or isdigit(char)

def isspace(char):
	""" Indicates if the char is a space, tabulation or new line """
	if char == " " or char == "\t" or char == "\n" or char == "\r":
		return True
	return False

def ispunctuation(char):
	""" Indicates if the char is a punctuation """
	if  (ord(char) >= 0x21 and ord(char) <= 0x2F) or \
		(ord(char) >= 0x3A and ord(char) <= 0x40) or \
		(ord(char) >= 0x5B and ord(char) <= 0x60) or \
		(ord(char) >= 0x7B and ord(char) <= 0x7E):
		return True
	else:
		return False

def dump(buff, withColor=True):
	""" dump buffer """
	if withColor:
		string = "\x1B[7m"
	else:
		string = ""
	if type(buff) == type(b"") or type(buff) == type(bytearray()):
		for i in buff:
			if isascii(chr(i)):
				string += chr(i)
			else:
				string += "\\x%02x"%i
	else:
		for i in buff:
			if isascii(i):
				string += i
			else:
				string += "\\x%02x"%ord(i)
	if withColor:
		string += "\x1B[m"
	return string

def dump_line (data, line = None, width = 0):
	""" dump a data data in hexadecimal on one line """
	size = len(data)
	fill = 0

	# Calculation of the filling length
	if width > size:
		fill = width-size

	# Displaying values in hex
	for i in data:
		line.write(b'%02X ' % i)

	# Filling of vacuum according to the size of the dump
	line.write(b'   '*fill)

	# Display of ASCII codes
	line.write(b' |')

	for i in data:
		if i >= 0x20 and  i < 0x7F:
			line.write(chr(i).encode("utf8"))
		else:
			line.write(b'.')

	# Filling of vacuum according to the size of the dump
	line.write(b' '*fill)

	# End of data ascii
	line.write(b'|')

def makedir(directory, recursive=False):
	""" Make directory recursively """
	if recursive is False:
		os.mkdir(directory)
	else:
		directories = [directory]
		while 1:
			parts = split(directory)
			if parts[1] == "" or parts[0] == "":
				break
			directories.append(parts[0])
			directory = parts[0]

		directories.reverse()
		for d in directories:
			if not(exists(d)):
				os.mkdir(d)

def tobytes(datas, encoding="utf8"):
	""" Convert data to bytes """
	result = datas
	if type(datas) == type(""):
		result = datas.encode(encoding)
	elif type(datas) == type([]):
		result = []
		for item in datas:
			result.append(tobytes(item, encoding))
	elif type(datas) == type((0,0)):
		result = []
		for item in datas:
			result.append(tobytes(item, encoding))
		result = tuple(result)
	elif type(datas) == type({}):
		result = {}
		for key, value in datas.items():
			result[tobytes(key,encoding)] = tobytes(value, encoding)
	return result

def tostrings(datas, encoding="utf8"):
	""" Convert data to strings """
	result = datas
	if type(datas) == type(b""):
		result = datas.decode(encoding)
	elif type(datas) == type([]):
		result = []
		for item in datas:
			result.append(tostrings(item, encoding))
	elif type(datas) == type((0,0)):
		result = []
		for item in datas:
			result.append(tostrings(item, encoding))
		result = tuple(result)
	elif type(datas) == type({}):
		result = {}
		for key, value in datas.items():
			result[tostrings(key,encoding)] = tostrings(value, encoding)
	return result

def tofilename(filename):
	""" Replace forbid characters in filename """
	filename = tostrings(filename)
	if len(filename) > 0:
		for char in "<>:/\\|?*":
			filename = filename.replace(char,"_%d_"%ord(char))
	return filename

def iscamera():
	""" Indicates if the board is esp32cam """
	try:
		import camera
		return camera.isavailable()
	except:
		if ismicropython():
			return False
		else:
			return True

def iptoint(ipaddr):
	""" Convert ip address into integer """
	spl = ipaddr.split(".")
	if len(spl):
		return ((int(spl[0])<<24)+ (int(spl[1])<<16) + (int(spl[2])<<8) + int(spl[3]))
	return 0

def issameinterface(ipaddr, ipinterface, maskinterface):
	""" indicates if the ip address is on the selected interface """
	ipaddr = iptoint(ipaddr)
	ipinterface  = iptoint(ipinterface)
	maskinterface = iptoint(maskinterface)
	if ipaddr & maskinterface == ipinterface & maskinterface:
		return True
	else:
		return False

def scandir(path, pattern, recursive, displayer=None):
	""" Scan recursively a directory """
	filenames   = []
	directories = []
	if path == "":
		path = "."
	try:
		if path is not None and pattern is not None:
			for file in os.listdir(path):
				if path != "":
					filename = path + "/" + file
				else:
					filename = file
				filename = filename.replace("//","/")
				filename = filename.replace("//","/")
				if isdir(filename):
					if displayer:
						displayer.show(filename)
					else:
						directories.append(filename)
					if recursive:
						dirs,fils = scandir(filename, pattern, recursive, displayer)
						filenames += fils
						directories += dirs
				else:
					if fnmatch.fnmatch(file, pattern):
						if displayer:
							displayer.show(filename)
						else:
							filenames.append(filename)
	except Exception as err:
		syslog(err)
	return directories, filenames

def remove(filename):
	""" Remove file existing """
	try:
		uos.remove(filename)
	except:
		pass

def rename(old, new):
	""" Rename file """
	if exists(new):
		remove(new)
	try:
		uos.rename(old, new)
	except:
		pass

up_last=0
up_total=0

def uptime(text="days"):
	""" Tell how long the system has been running """
	global up_last, up_total
	try:
		# pylint: disable=no-member
		up = time.ticks_ms()
	except:
		up = time.time() * 1000

	if up_last > up:
		up_total += 1^30

	up_last = up
	up += up_total

	millis  = (up%1000)
	seconds = (up/1000)%60
	mins    = (up/1000/60)%60
	hours   = (up/1000/3600)%24
	days    = (up/1000/86400)
	return "%d %s, %d:%02d:%02d"%(days, tostrings(text),hours,mins,seconds)

def reboot(message="Reboot"):
	""" Reboot command """
	syslog(message)
	from tools.lang import RegionConfig
	region_config = RegionConfig()
	if region_config.load():
		region_config.current_time = time.time() + 8
		region_config.save()
	try:
		if ismicropython():
			import camera
			camera.deinit()
	except:
		pass
	machine.deepsleep(1000)
