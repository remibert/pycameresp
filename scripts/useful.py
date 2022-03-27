#!/usr/bin/env python3
# coding: utf-8
from __future__ import print_function, absolute_import, unicode_literals
from  io import StringIO, BytesIO

def is_python2():
	from sys import version_info
	if version_info.major >= 3:
		return False
	return True

def is_python3():
	from sys import version_info
	if version_info.major >= 3:
		return True
	return False

def to_char(integer):
	""" Convert integer into charactere 
	>>> ord(to_char(1))
	1
	>>> ord(to_char(0x80))
	128
	"""
	if integer >= 0x80:
		return eval(u"'\\x%02X'"%integer)
	else:
		return chr(integer)

def to_bytes(data):
	""" Convert data into bytes latin-1 
	>>> print(to_string(to_bytes("abcde")))
	abcde
	"""
	if is_bytes(data):
		return data
	else:
		return data.encode("latin-1")

def to_string(data):
	""" Convert bytes into string
	>>> s = ""
	>>> for ch in range(256): s += to_char(ch)
	>>> b = to_bytes(s)
	>>> is_bytes(b)
	True
	>>> ss = to_string(b)
	>>> for i in range(256):
	...    if ord(s[i]) != ord(s[i]):
	...       print("Err in %d"%i)
	"""
	if is_string(data):
		return data
	else:
		return data.decode("latin-1")

def is_string(data):
	""" Indicates if the data is a string
	>>> is_string("str")
	True
	>>> is_string(u"jjj")
	True
	>>> is_string(12)
	False
	"""
	try:
		from types import UnicodeType, StringType
		if type(data) == UnicodeType or type(data) == StringType:
			return True
	except ImportError:
		if type(data) == type(""):
			return True
	return False

def is_bytes(data):
	""" Indicates if the data is a string
	>>> is_bytes(b"str")
	True
	>>> is_bytes(u"jjj")
	False
	>>> is_string(12)
	False
	"""
	try:
		from types import BytesType
		if type(data) == BytesType:
			return True
	except ImportError:
		if type(data) == type(b""):
			return True
	return False

def is_integer(data):
	""" Indicates if the data is an integer
	>>> is_integer("str")
	False
	>>> is_integer(u"jjj")
	False
	>>> is_integer(12)
	True
	"""
	try:
		from types import LongType, IntType
		if type(data) == LongType or type(data) == IntType:
			return True
	except ImportError:
		if type(data) == type(int(0)):
			return True
	return False

def is_tuple(data):
	""" Indicates if the data is a tuple 
	>>> is_tuple((0,0))
	True
	>>> is_tuple([])
	False
	>>> is_tuple({})
	False
	"""
	try:
		from types import TupleType
		if type(data) == TupleType:
			return True
	except ImportError:
		if type(data) == type((0,0)):
			return True
	return False

def is_list(data):
	""" Indicates if the data is a list
	>>> is_list((0,0))
	False
	>>> is_list([])
	True
	>>> is_list({})
	False
	"""
	try:
		from types import ListType
		if type(data) == ListType:
			return True
	except ImportError:
		if type(data) == type([]):
			return True
	return False

def is_dict(data):
	""" Indicates if the data is a list
	>>> is_dict((0,0))
	False
	>>> is_dict([])
	False
	>>> is_dict({})
	True
	"""
	try:
		from types import DictType
		if type(data) == DictType:
			return True
	except ImportError:
		if type(data) == type({}):
			return True
	return False

def to_integer(data):
	""" Convert character into integer"""
	if is_integer(data):
		return data
	else:
		return ord(data)

def adapt_path(path):
	from sys import platform
	if platform != "win32":
		return path.replace("\\","/")
	return path

def indent(node, file = None, deep = 0):
	""" Indent a python collection 
	>>> print(indent([123,{"893":[123,{"456":456},(789,123)]},(789,123)]))
	[
	    123
	    {
	        "893":
	        [
	            123
	            {
	                "456"                : 456
	            }
	            (
	                789
	                123
	            )
	        ]
	    }
	    (
	        789
	        123
	    )
	]
	<BLANKLINE>
	"""
	if file == None:
		output = StringIO()
	else:
		output = file
	
	indentType = "    "
	if is_list(node):
		output.write("%s[\n"%(indentType*deep))
		for item in node:
			indent(item, output, deep + 1)
		output.write("%s]\n"%(indentType*deep))
	elif is_tuple(node):
		output.write("%s(\n"%(indentType*deep))
		for item in node:
			indent(item, output, deep + 1)
		output.write("%s)\n"%(indentType*deep))
	elif is_dict(node):
		output.write("%s{\n"%(indentType*deep))
		for key, value in node.items():
			if is_tuple(value) or is_list(value) or is_dict(value):
				output.write('%s"%s":\n'%(indentType*(deep+1), key))
				indent(value, output, deep+1)
			else:
				output.write('%s%-20s : %s\n'%(indentType*(deep+1), '"%s"'%key, repr(value)))
		output.write("%s}\n"%(indentType*deep))
	else:
		output.write("%s%s\n"%(indentType*deep, repr(node)))
	
	if file == None:
		return output.getvalue()
	else:
		return None

def str_to_dec(string):
	""" Convert a string into decimal value 
	>>> print (str_to_dec("123"))
	123
	>>> print (str_to_dec("0123"))
	123"""
	string = string.lstrip("0")
	if len(string) == 0:
		return 0
	else:
		return eval(string)

def makedir (directory):
	""" Create directory """
	from os import makedirs
	from os.path import exists
	directory = adapt_path(directory)
	if directory != "" and not exists(directory):
		for i in range(10,0,-1): # Insiste!
			try:
				makedirs(directory)
			except OSError as val:
				if not exists(directory):
					print ("Retry make dir %s"%directory)
					if i <= 1:
						if val.errno != 17:
							raise val
				else:
					break

class CommandLauncher:
	def __init__(self):
		self.running = False
		self.lines = []
		self.aborted = False

	def execute_one(self, command, output = None, encoding = None, inactivityDuration = None):
		from useful     import adapt_path
		from subprocess import Popen, PIPE
		from sys        import platform
		from threading  import Timer

		command = adapt_path(command)

		if inactivityDuration != None:
			inactivityTimer = Timer(inactivityDuration, self.inactivity_timeout)
			inactivityTimer.start()
		else:
			inactivityTimer = None
		
		if encoding == None:
			if platform == "win32":
				encoding = "cp437"
			else:
				encoding = "utf-8"
		
		def __write_output(message, output):
			if (output):
				if type(output) == type(True):
					if output == True:
						print (message.rstrip())
				else:
					try:
						output.write(message.rstrip() + "\n")
					except:
						message = message.encode('cp850','replace').decode('cp850')
						output.write(message.rstrip() + "\n")
					output.flush()
		
		self.lines.append("> %s"%command)
		__write_output("> %s"%command, output)

		try:
			timerStarted = 0
			
			self.process = Popen(args=command, stdout=PIPE, stderr=STDOUT, shell=True)
			
			while True:
				line = self.process.stdout.readline()

				# Restart the inactivity timer for a group line (avoid cpu load)
				if timerStarted > 20:
					inactivityTimer.cancel()
					inactivityTimer = Timer(inactivityDuration, self.inactivity_timeout)
					inactivityTimer.start()
					timerStarted = 0

				# Check if the process is terminated
				if len(line) == 0 and self.process.poll() != None:
					# Process ended
					break

				elif type(line) == bytes:
					try:
						decoded = line.decode(encoding)
					except UnicodeEncodeError:
						decoded = line.decode("utf-8","ignore")
					line = decoded
					
					# Add lines in output list
					self.lines.append(line[:-1])
				if len(line) > 0:
					__write_output(line, output)
		finally:
			self.process = None
			if inactivityTimer:
				inactivityTimer.cancel()

	def inactivity_timeout(self):
		if self.process != None:
			print("!~ Inactivity timeout, process killed")
			self.process.kill()

	def execute_many(self, commands, output=True, encoding=None, inactivityDuration=None, thread=False):
		import threading
		from useful import is_string
		if is_string(commands):
			commands = [commands]
		if thread == True:
			threading.Thread(target = self.execute_thread, kwargs={
				"commands"          : commands,
				"output"            : output,
				"encoding"          : encoding, 
				"inactivityDuration": inactivityDuration
				}).start()
			return None
		else:
			self.execute_thread(commands, output, encoding, inactivityDuration)
			return self.lines

	def execute_thread(self, commands, output, encoding, inactivityDuration):
		if self.running == False:
			self.running = True
			self.aborted = False
			self.lines = []
			for commandBlock in commands:
				if self.aborted == True:
					break
				for command in commandBlock.split("\n"):
					if self.aborted == True:
						break
					self.execute_one(command, output, encoding, inactivityDuration)
			if self.aborted:
				print ("=== ABORTED ===\n")
			self.running = False
		else:
			print ("!~ Previous command in progress")

	def abort(self):
		self.aborted = True

def execute(commands, output = None, encoding = None, inactivityDuration = None, thread=False):
	""" Starts the execution of a process
	>>> from sys import platform
	>>> cmd = 'ls'
	>>> if platform == "win32" : cmd = 'dir'
	>>> res = execute(cmd)
	>>> len(res) > 10
	True"""
	process = CommandLauncher()
	return process.execute_many(commands, output, encoding, inactivityDuration, thread)

def execute2(command, output = None, encoding=None):
	execute(command, output, encoding)

def get_file_modif_time(filename):
	""" Gets the modification time of file 
	>>> makedir("testunit")
	>>> r=open("testunit/toto.txt","w").write("Hello") 
	>>> get_file_modif_time("testunit/toto.txt") > 0
	True
	>>> import os
	>>> os.remove("testunit/toto.txt")
	"""
	filename = adapt_path(filename)
	from os import stat
	try:
		result = stat(filename).st_mtime
	except:
		result = 0
	return result

def get_file_size(filename):
	""" Gets the size of file
	>>> makedir("testunit")
	>>> r=open("testunit/toto.txt","w").write("Hello")
	>>> get_file_size("testunit/toto.txt") == 5
	True
	>>> import os
	>>> os.remove("testunit/toto.txt")
	"""
	filename = adapt_path(filename)
	from os import stat
	from stat import ST_SIZE
	return stat(filename)[ST_SIZE]

def del_doublon(values):
	""" delete duplicated data in list 
	>>> a = [1,2,2,3,3,4,4,4,5,5,6]
	>>> del_doublon(a)
	[1, 2, 3, 4, 5, 6]"""
	return list(set(values))

def get_username():
	from os import environ
	return environ["USERNAME"]

def copy_file(source, target):
	""" Copy file 
	>>> makedir("testunit")
	>>> r=open("testunit/toto_.txt", "w").write("PRout") 
	>>> copy_file("testunit/toto_.txt","testunit/titi.txt")
	>>> int(get_file_modif_time("testunit/titi.txt")) == int(get_file_modif_time("testunit/toto_.txt"))
	True
	>>> get_file_modif_time("testunit/titi.txt") > 0
	True
	>>> copy_file("testunit/toto_.txt","testunit/titi.txt")
	>>> import os
	>>> os.remove("testunit/titi.txt")
	>>> os.remove("testunit/toto_.txt")
	"""
	from shutil import copyfile, copystat, copymode
	from os.path import split
	source = adapt_path(source)
	target = adapt_path(target)
	if int(get_file_modif_time(source)) != int(get_file_modif_time(target)):
		makedir(split(target)[0])
		copyfile(source, target)
		copystat(source, target)
		copymode(source, target)
	#~ else:
		#~ print ("%s not copied"%(target))

def copy_files(sourceDir, destinationDir, patterns):
	""" Copy files
	remove_dir("testunit")
	makedir("testunit/Test123")
	r=open("testunit/Test123/123.txt","w").write("123")
	copy_files("testunit/Test123","testunit/Test456","*.*")
	remove_dir("testunit/Test456")
	"""
	from glob import glob
	from os.path import join, abspath, exists, isfile
	import shutil
	sourceDir      = adapt_path(sourceDir)
	destinationDir = adapt_path(destinationDir)
	
	if exists(abspath(sourceDir)) == False:
		print ('! "%s" directory not existing'%sourceDir)
	makedir(destinationDir)
	for pattern in patterns:
		srcPath = join(sourceDir,pattern)
		for filename in glob(srcPath):
			if isfile(filename):
				try:
					shutil.copy2(filename, destinationDir)
				except IOError:
					print ("! Failed copy '%s' -> '%s'" %(filename, destinationDir))

def remove_dir(directory):
	""" Remove directory and its content """
	import shutil
	import os
	from time import sleep
	from os.path import exists
	directory      = adapt_path(directory)
	while exists(directory):
		try:
			shutil.rmtree(directory,0,lambda function,directory,dummy: (os.chmod(directory, 0o777),os.remove(directory)))
		except OSError:
			print ("! Remove dir failed '%s'"%directory)
		if exists(directory):
			sleep(1)

def delete_files(directory, patterns):
	""" Delete files 
	>>> makedir("testunit/Test123")
	>>> r=open("testunit/Test123/123.txt","w").write("123")
	>>> r=open("testunit/Test123/123.tot","w").write("123")
	>>> makedir("testunit/Test123/456")
	>>> r=open("testunit/Test123/456/456.txt","w").write("456")
	>>> delete_files("testunit/Test123","*.burp")
	>>> get_file_modif_time("testunit/Test123/123.txt") > 0
	True
	>>> get_file_modif_time("testunit/Test123/123.tot") > 0
	True
	>>> delete_files("testunit/Test123",["*.tot"])
	>>> get_file_modif_time("testunit/Test123/123.txt") > 0
	True
	>>> get_file_modif_time("testunit/Test123/123.tot") > 0
	False

	>>> makedir("testunit/Test123")
	>>> r=open("testunit/Test123/123.txt","w").write("123")
	>>> r=open("testunit/Test123/123.tot","w").write("123")
	>>> makedir("testunit/Test123/456")
	>>> r=open("testunit/Test123/456/456.txt","w").write("456")
	>>> delete_files("testunit/Test123",["*.tot","*.txt"])
	>>> get_file_modif_time("testunit/Test123/123.txt") > 0
	False
	>>> get_file_modif_time("testunit/Test123/123.tot") > 0
	False
	>>> remove_dir("testunit/Test123")
	"""
	from glob import glob
	from os.path import join
	from os import remove
	directory      = adapt_path(directory)
	if is_string(patterns):
		patterns = [patterns]
	for pattern in patterns:
		for filename in glob(join(normalize_path(directory), pattern)):
			try:
				remove(filename)
			except OSError:
				print ("! Failed delete '%s'"%filename)

def compare(file1, file2):
	""" Compare two files content
	>>> makedir("testunit")
	>>> r=open("testunit/1234.txt","w")
	>>> l=r.write("123")
	>>> r.close()
	>>> r=open("testunit/4567.txt","w")
	>>> l = r.write("123")
	>>> r.close()
	>>> compare("testunit/1234.txt","testunit/4567.txt")
	True
	>>> copy_file("testunit/1234.txt","testunit/4567.txt")
	>>> compare("testunit/1234.txt","testunit/4567.txt")
	True
	>>> r=open("testunit/4567.txt","w")
	>>> l = r.write("124")
	>>> r.close()
	>>> compare("testunit/1234.txt","testunit/4567.txt")
	False
	>>> delete_files(".",["testunit/1234.txt","testunit/4567.txt"])
	"""
	from os.path import exists
	result = False
	
	file1      = adapt_path(file1)
	file2      = adapt_path(file2)
	
	# If two files existing
	if exists(file1) and exists(file2):
		# If the date and size equal
		if get_file_size(file1) == get_file_size(file2):
			try:
				# Read the content of first file
				content1 = open(file1, "rb").read()
				try:
					# Read the content of second file
					content2 = open(file2, "rb").read()
					# If content differs
					if content1 == content2:
						result = True
				except IOError:
					pass
			except IOError:
				pass
	return result

def update_file(filename, content):
	""" Update a file with content 
	>>> makedir("testunit")
	>>> r=open("testunit/toto.txt","w").write("prout")
	>>> print(update_file("testunit/toto.txt","burp"))
	burp
	>>> print(update_file("testunit/toto.txt","burp"))
	burp
	>>> import os
	>>> os.remove("testunit/toto.txt")
	"""
	filename      = adapt_path(filename)
	if filename != None:
		try:
			oldContent = open(filename, "r").read()
		except IOError:
			oldContent = ""
		if oldContent != content:
			file = open (filename, "w")
			file.write(content)
			file.close()
	return content

def get_directory(path):
	""" Gets directory name
	>>> r = get_directory("testunit/Test123/123.txt")
	>>> r in ('testunit/Test123','testunit\Test123')
	True
	"""
	from os.path import split
	path = normalize_path(path)
	return split(path)[0]

def get_filename(path):
	""" Gets file name
	>>> print(get_filename("testunit/Test123/123.txt"))
	123.txt
	"""
	from os.path import split
	path = normalize_path(path)
	return split(path)[1]

def get_extension(path):
	""" Gets extension of file
	>>> print(get_extension("testunit/Test123/123.txt"))
	.txt
	"""
	from os.path import splitext
	return splitext(path)[1]

def get_name(path):
	""" Gets name of file without extension
	>>> print(get_name("testunit/Test123/123.txt"))
	123
	"""
	from os.path import split, splitext
	path = normalize_path(path)
	return splitext(split(path)[1])[0]

def get_directory_filename(path):
	""" Gets complet path and filename without extension 
	>>> get_directory_filename("testunit/Test123/123/TOTO.txt") in ['testunit/Test123/123/TOTO','testunit\\\\Test123\\\\123\\\\TOTO']
	True
	"""
	from os.path import splitext
	path = normalize_path(path)
	return splitext(path)[0]

def get_script_path(*p):
	""" Gets the path of the script
	>>> path = get_script_path("./useful.py")
	>>> get_name(path) == "useful"
	True
	>>> len(get_directory(path)) > 0
	True
	"""
	from os.path import abspath, dirname, join
	result = normalize_path(abspath(dirname(__file__)))
	if len(p) > 0:
		return normalize_path(join(result, *p))
	return result

def get_current_path(*p):
	""" Gets the current path """
	from os.path import join
	from os import getcwd
	result = getcwd()
	if len(p) > 0:
		return join(result, *p)
	return result

def get_abs_path(*p):
	"""Gets absolute path
	>>> r=open("testunit/toto.txt","w").write("Hello")
	>>> len(get_abs_path("dir","testunit/toto.txt")) > 10
	True
	>>> import os
	>>> os.remove("testunit/toto.txt")
	"""
	from os.path import abspath, join
	if len(p) >= 1:
		return normalize_path(join(abspath(p[0]), *p))
	return ""

def get_recent_file(*p):
	""" Gets more recent file in the file list
	>>> from time import sleep
	>>> r=open("testunit/One.txt","w").write("One")
	>>> sleep(1)
	>>> r=open("testunit/Two.txt","w").write("two")
	>>> get_recent_file("./testunit/","*.txt") in ['./testunit/Two.txt', '.\\\\testunit\\\\Two.txt', './testunit\\\\Two.txt']
	True
	>>> import os
	>>> os.remove("testunit/One.txt")
	>>> os.remove("testunit/Two.txt")
	"""
	from os import stat
	from os.path import join
	from glob import glob
	result = ""
	files = glob(join(p[0],*p[1:]))
	for file in files:
		if result == "":
			result = file
		else:
			if stat(file).st_mtime > stat(result).st_mtime:
				result = file
	return result

def normalize_list(lst):
	from os import sep
	result = []
	
	if is_string(lst):
		lst = [lst]
	
	for item in lst:
		if sep == "/":
			tmp = item.replace("\\",sep)
		else:
			tmp = item.replace("/",sep)
		result.append(adapt_path(tmp))
	return result

def scan_all(directory, includes = ["*"], excludes = []):
	""" Parse a directory and returns the list of files and directories """
	from os import walk
	from os.path import join
	
	excludes = normalize_list(excludes)
	includes = normalize_list(includes)
	directory = adapt_path(directory)
	
	def add(filename, includes, excludes, lst):
		from fnmatch import fnmatchcase
		from os.path import split
		excluded = None
		included = None
		adding = False
		
		for exclude in excludes:
			if fnmatchcase (filename, exclude):
				excluded = (filename, exclude)
				break
			else:
				if fnmatchcase (split(filename)[1], exclude):
					excluded = (split(filename)[1], exclude)
					break
		
		for include in includes:
			if fnmatchcase (filename, include):
				included = (filename, include)
				break
			else:
				if fnmatchcase (split(filename)[1], include):
					included = (split(filename)[1], include)
					break
		
		if excluded == None and included != None:
			adding = True
		elif excluded != None and included == None:
			pass
		elif excluded != None and included != None:
			a = fnmatchcase(excluded[1],included[1])
			b = fnmatchcase(included[1],excluded[1])
			
			if a and not b:   pass
			elif not a and b: adding = True
			elif a and b:     adding = True
		if adding:
			lst.append(filename)
	
	if   is_string(includes)      : includes = [includes]
	elif type(includes) == type(None): includes = []
		
	if   is_string(excludes)      : excludes = [excludes]
	elif type(excludes) == type(None): excludes = []
	
	files = []
	directories = []
	for i in walk(directory):
		dirpath, dirnames, filenames = i
		for dirname in dirnames:
			add(join(dirpath, dirname), includes, excludes, directories)
			
		for filename in filenames:
			add(join(dirpath, filename), includes, excludes, files)
	all_ = directories + files
	return all_, files, directories

def scan_files(directory, includes = ["*"], excludes = []):
	""" List files
	>>> scan_files("..","Con*.py","Color*.py")[0] in (u'..\\\\rbtools\\\\Console.py',"../rbtools/Console.py")
	True
	"""
	return scan_all(directory, includes, excludes)[1]

def scan_directories(directory, includes = ["*"], excludes = []):
	""" List directories
	>>> len(scan_directories("../application")) > 10
	True
	"""
	return scan_all(directory, includes, excludes)[2]

def prefix(files):
	""" Gives the common prefix of a file set 
	>>> files = ["/titi/tutu/tata/toto.txt","/titi/tutu/toto.txt","/titi/tutu/tete/toto.txt","/titi/tutu/tout/toto.txt","/titi/tutu/.txt","/titi/tutu/tutu/toto.txt"]
	>>> prefix(files) in ['/titi/tutu','\\\\titi\\\\tutu']
	True
"""
	from os import sep
	
	# Initializes counters
	counters = []
	
	# For all files
	for file in files:
		file = normalize_path(file)
		
		# Split the file name into a piece
		paths = file.split(sep)
		
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
				result += list(counter.keys())[0] + sep
			else:
				return result [:-1]
				break
		return result
	except IndexError:
		return ""

def zip_dir(nameOrFile, directory, includes = ["*"], excludes = [], display = False, renames = None):
	""" Unflat the directory 
	>>> makedir("testunit")
	>>> zip_dir("testunit/zip.zip","./rbtools","Co*.py","Color*.py",True)
	testunit/zip.zip ./rbtools Co*.py Color*.py
	>>> remove_dir("testunit")
	"""
	from zipfile import ZipFile, ZIP_DEFLATED 
	from os.path import commonprefix, split, relpath, splitext

	previousDir = ""
	previousExt = []
	if display and is_string(nameOrFile):
		print (nameOrFile, directory, includes, excludes)

	# Search all files according patterns
	all_ = scan_all(directory, includes, excludes)[0]

	# If the output filename detected
	if is_string(nameOrFile):
		if split(nameOrFile)[0] != "":
			makedir(split(nameOrFile)[0])

	prefix = split(normalize_path(commonprefix(all_)))[0]
	
	# Create archive file
	archive = ZipFile(nameOrFile,"w", ZIP_DEFLATED)
	
	# For all files found
	for source in all_:
		# If some progress information must be displayed
		if display:
			directory = split(source)[0]
			extension = splitext(source)[1]
			
			# If the directory changed
			if previousDir != directory:
				print ("\n",directory)
				previousDir  = directory
				previousExt = []
			
			# If the extension not yet displayed
			if not extension in previousExt:
				print (extension, end=" ")
				previousExt.append(extension)
		
		# Build the destination zip name without the prefix
		destination = relpath(source, prefix)
		
		# If some destination directory must be renamed
		if renames:
			for old, new in renames:
				destination = destination.replace(old, new)
		
		try:
			archive.write(source, destination)
		except IOError:
			print ('! Cannot add file "%s" in the archive'%source)
		except OSError:
			print ('! Cannot add file "%s" in the archive'%source)
	
	if not is_string(nameOrFile):
		return nameOrFile.getvalue()
	else:
		return None

def mini(a,b):
	""" Minimal value
	>>> mini(3,4)
	3
	"""
	if a < b: 
		return a
	return b

def maxi(a,b):
	""" Maximal value
	>>> maxi(3,4)
	4
	"""
	if a > b: 
		return a
	return b

def relatif (path, root = None):
	""" Makes relative an absolute path
	>>> relatif("C:/tyty/uuuu/vvvv/titi/tutu/toto","C:/tyty/uuuu/vvvv/titi") in ["tutu/toto","tutu\\\\toto"]
	True
	>>> relatif("C:/tyty/titi/tata","C:/tyty/titi/tutu/toto") in ["../../tata", "..\\\\..\\\\tata"]
	True
	>>> relatif("C:/titi/tutu","E:/titi") in  ["C:/titi/tutu", "C:\\\\titi\\\\tutu"]
	True
	>>> relatif("C:/titi/tutu","") in ["C:/titi/tutu", "C:\\\\titi\\\\tutu"]
	True
	>>> relatif("C:/tyty/uuuu/vvvv/titi/tutu/toto/","C:/tyty/uuuu/vvvv/titi") in ["tutu/toto", "tutu\\\\toto"]
	True
	>>> relatif("C:/tyty/titi/tata/","C:/tyty/titi/tutu/toto") in ["../../tata", "..\\\\..\\\\tata"]
	True
	>>> relatif("C:/titi/tutu/","E:/titi") in ["C:/titi/tutu", "C:\\\\titi\\\\tutu"]
	True
	>>> relatif("C:/titi/tutu/","") in ["C:/titi/tutu", "C:\\\\titi\\\\tutu"]
	True
"""
	from os import sep, getcwd
	path = normalize_path(path)
	if root != None:
		root =normalize_path(root)
	# If the path is empty
	if len(path) == 0:
		return ""

	# If the root is not defined
	if root == None:
		# Take the current directory
		root = getcwd()
		
	# Cut paths to directory
	if path[-1] == sep:
		path = path[:-1]
	spPath = path.split(sep)
	spRoot = root.split(sep)

	# Constructs the list of the identical path
	equal = []
	for i in range(0,mini(len(spRoot),len(spPath))):
		if spRoot[i] != spPath[i]:
			break
		else:
			equal.append(spPath[i])

	# If the identical list is not empty
	if len(equal) != 0:
		# Remove identical paths 
		spRoot = spRoot[len(equal):]
		spPath = spPath[len(equal):]
		
		# Add an indirection
		for i in range(len(spRoot)):
			spPath.insert(0,"..")

	# Constructs the relative path
	result = ""
	for i in spPath:
		result += i + sep

	if result != "":
		return result[:-1]
	else:
		return ""

def filename_split (p):
	""" Split filename 
	>>> print("('%s', '%s', '%s', '%s')"%filename_split("/toto/titi/tutu.tata"))
	('', '/toto/titi', 'tutu', '.tata')
	"""
	from os.path import split as splitPath, splitdrive, splitext
	
	splt = splitPath (p)
	disk,dir_ = splitdrive(splt[0])
	try:
		if disk[1] != ":":
			raise IndexError
	except IndexError:
		disk,dir_ = "", splt[0]
	name,ext = splitext(splt[1])
	return disk,dir_,name,ext

def convert_filename (pattern, name):
	""" Convert filename according to the pattern specified 
	>>> convert_filename ("*","toto")      == "toto"
	True
	>>> convert_filename ("?a*","toto")    == "tato"
	True
	>>> convert_filename ("?a?","toto")    == "tat"
	True
	>>> convert_filename ("i??","toto")    == "iot"
	True
	>>> convert_filename ("*","toto")      == "toto"
	True
	>>> convert_filename ("?i?*","uuuuuu") == "uiuuuu"
	True
	>>> convert_filename ("toto","huhu")   == "toto"
	True
	>>> convert_filename ("t","huhu")      == "t"
	True
	"""
	result = ""
	j = 0
	i = 0
	while j < len (pattern) or i < len(name):
		# If the format ended 
		if j >= len (pattern):
			break
		# If one charactere must be ignored 
		elif pattern [j] == '?':
			if i < len(name):
				result = result + name [i]
				i += 1
			if j < len(pattern):
				j += 1
		# If one or more characteres must be ignored 
		elif pattern [j] == '*':
			if i < len(name):
				result = result + name [i]
				i += 1
			else :
				break
		else:
			if i < len(name):
				i += 1

			if j < len(pattern):
				result = result + pattern [j]
				j += 1
	return result

def convert_path (source, target, filename):
	""" Convert source path into target path 
	>>> convert_path ("/Remi/Source/Python/Application/*.*","tutu/titi/*.*","Remi/Source/Python/Application/path/lkjlk/Modem.old") in ["tutu/titi/path/lkjlk/Modem.old", 'tutu\\\\titi\\\\path\\\\lkjlk\\\\Modem.old']
	True
	>>> convert_path ("/Remi/Source/Python/Application/*.ui","/titi/tutu/*.bu","/Remi/Source/Python/Application/TraceOut/UserInterface/frmTraceOut.ui") in ["/titi/tutu/TraceOut/UserInterface/frmTraceOut.bu", '\\\\titi\\\\tutu\\\\TraceOut\\\\UserInterface\\\\frmTraceOut.bu']
	True
	>>> convert_path ("/Remi/Source/Python/Application/*.ui","/titi/tutu/*.bu","/Remi/Source/Python/Application/TraceOut/UserInterface/frmTraceOut.ui") in ["/titi/tutu/TraceOut/UserInterface/frmTraceOut.bu", "\\\\titi\\\\tutu\\\\TraceOut\\\\UserInterface\\\\frmTraceOut.bu"]
	True
	>>> convert_path ("/Remi/Source/Python/Application/*.ui","titi/tutu/*.bu","/Remi/Source/Python/Application/TraceOut/UserInterface/frmTraceOut.ui") in ["titi/tutu/TraceOut/UserInterface/frmTraceOut.bu", "titi\\\\tutu\\\\TraceOut\\\\UserInterface\\\\frmTraceOut.bu"]
	True
	"""
	from os.path import join as joinPath
	from os import sep

	# Get the source path informations
	dirSrc = filename_split (source)[1]

	# Get the target path informations
	diskDst, dirDst, nameDst, extDst = filename_split (target)

	# Get the current file informations
	dummy, dirFil, nameFil, extFil = filename_split (filename)

	# Build the target path
	dir_ = normalize_path(dirDst + sep + dirFil[len(dirSrc):len(dirSrc) + len(dirFil)-len(dirSrc)])

	# Add the target filename
	name =  convert_filename (nameDst,nameFil)

	# Add the target extension
	ext = convert_filename (extDst,extFil)

	return diskDst + joinPath(dir_, name + ext)

def replace_in_file (remplacements, source, destination, replaceInReadOnly = 0, confirm = None):
	""" Performs string replacements in a file 
		Replacements: tuple list [("search", "replace with"), (...)]
		Source: name of the source file
		Destination: destination file name
	"""
	from shutil import copy2
	from os.path import isdir, exists, split as splitPath
	from os import access, W_OK, chmod

	source      = adapt_path(source)
	destination = adapt_path(destination)
	
	# If it is not a file
	if isdir (source) or isdir (destination):
		return

	# Clears the contents of the target file
	result =[]
	modified = 0
	lineNumber = 0

	if remplacements != []:
		try:
			# Reading the contents of the file and creating a list of lines
			sourceLines = open(source,"r").readlines()

			# For each line in the original file
			for line in sourceLines:
				# For each replacement to be made in the original file
				for i in remplacements:
					# Replaces values in line
					res = line.replace(i[0], i[1])

					# Inhibits updating the line
					update = 0

					# If there has been a replacement
					if line.find(i[0]) != -1:
						# If confirmation is not required
						if confirm == None:
							update = 1
						# If the change is confirmed
						elif confirm (source, lineNumber, sourceLines, i[0]) == 1:
							update = 1

					# If an update of the current line is requested
					if update:
						# The file must be updated
						modified = 1

						# Updated line modified
						line = res

				# Adds the new line to the target file
				result.append(line)

				# Increment the current line number
				lineNumber += 1
		except UnicodeDecodeError:
			# Replacement in binary file disabled
			modified = 0

	# If the file is to be saved
	if modified:
		# If replacement is force for protected files
		if replaceInReadOnly:
			# Deletes read-only
			chmod(destination, 0o777)
		# If the file is not write-protected
		if access(destination, W_OK) == 1 or not exists(destination):
			# Opens and saves the lines of the target file
			open(destination,"w").writelines(result)
	# If the destination file is different from the source file
	elif source != destination:
		# Copies the destination file
		makedir (splitPath(destination)[0])
		try:   copy2(source, destination)
		except IOError:print ("Cannot copy %s->%s"%(source, destination))

def multi_line_replace_in_file (replaces, source, destination):
	""" Performs string replaces in a file
		replaces: tuple list [("search", "replaces with"), (...)]
		source: name of the source file
		destination: destination file name
	"""
	from os.path import isdir
	from os import chmod, rename, remove

	source      = adapt_path(source)
	destination = adapt_path(destination)
	
	# If it is not a file
	if isdir (source) or isdir (destination):
		return

	# Reading the contents of the file and creating a list of lines
	content = open(source,"rb").read()

	if is_bytes(content):
		content = content.decode("latin-1")
		bytesDetected = True
	else:
		bytesDetected = False
		
	# Browse the list of replacements
	for old, new in replaces:
		# Replaces the values in the file
		content = content.replace(old, new)
		
	if bytesDetected:
		content = content.encode()
	
	# Removes write protection
	try:   chmod (source, 0o777)
	except OSError:pass

	# Deletes read-only
	try:   chmod(destination, 0o777)
	except OSError:pass

	# If the source file needs to be modified
	if source == destination:
		# Backup file name
		backup = source + ".bak"

		# Deletes read-only from backup file
		try:   chmod (backup, 0o777)
		except OSError:pass
		
		# Deletes the backup file
		try:   remove (backup)
		except OSError:pass

		# Rename the file
		rename (source, source + ".bak")

	# Opens and saves the lines of the target file 
	open(destination,"wb").write(content)

def build_replace_list (remplacements, sourcePath, includes, excludes = [], destinationPath = None, replaceFilename = True):
	""" Constructs a file replacement list """
	from os import sep

	destinations = []

	# Analyzes the directories
	sources = scan_all(normalize_path(sourcePath), includes, excludes)[0]

	# If the destination directory is not defined
	if destinationPath == None:
		destinations = sources[:]
	else:
		destinations = []

		# Creation de la liste des fichiers de destination
		for source in sources:
			# Gets the destination directory name
			destination = normalize_path(destinationPath + sep + source[len (sourcePath):])

			# If file names are to be replaced
			if replaceFilename:
				# For each replacement to be made in the destination directory name
				for i in remplacements:
					# Replaces values in line 
					destination = destination.replace(i[0], i[1])

			# Adding the directory to the list
			destinations.append (normalize_path(destination))
	return sources, destinations

def multiFilesReplacements(
	replacements, 
	destinationPath     = "Generated" , 
	sourcePath          = "Data", 
	includes            = "*", 
	excludes            = [], 
	replaceFilename     = True, 
	multiLineReplacement= False):
	"""Replaces in the given files
	replacements: alternate list
	destinationPath: destination directory
	sourcePath: source directory of files
	includes: name of files to replace
	excludes: name of files to be ignored
	multiLineReplacement: to make multiline changes
	for example:
	multiFilesReplacements (
	replacements = [("oldstring", "newstring")],
	destinationPath = "new",
	sourcePath = "old",
	includes = "* .php",
	multiLineReplacement = True)
	>>> makedir("testunit/source")
	>>> makedir("testunit/dest")
	>>> r=open("testunit/source/totototoeuh.txt","wb").write(b"Hello totototoeuh\\nBonjour totototoeuh")
	>>> r=open("testunit/source/totototoeuh.text","wb").write(b"Hello totototoeuh\\nBonjour totototoeuh")
	>>> multiFilesReplacements(("totototoeuh","prout"),"testunit/dest","testunit/source","tototot*.t*","*.text",True,False)
	>>> f = open("testunit/dest/prout.txt","r")
	>>> data = f.read()
	>>> f.close()
	>>> print(data)
	Hello prout
	Bonjour prout
	>>> remove_dir("testunit/dest")
	>>> multiFilesReplacements(("totototoeuh\\nBonjour","prout"),"testunit/source","testunit/source","tototot*.t*","*.text",False,True)
	>>> f = open("testunit/source/totototoeuh.txt","r")
	>>> data = f.read()
	>>> f.close()
	>>> print(data)
	Hello prout totototoeuh
	>>> remove_dir("testunit")
	"""
	from os.path import isdir, exists
	
	# If this is not a replacement list
	if not is_tuple(replacements) and not is_list(replacements):
		return
	# If the list contains elements
	if len(replacements) > 0:
		# If this is a string list
		if is_string(replacements[0]):
			# Turns the string list into a pair list
			replacements = [replacements]
	# Constructs the destination list of files 
	sources, destinations = build_replace_list(replacements, sourcePath, includes, excludes, destinationPath, replaceFilename)

	# Creating the destination directory
	if not exists(destinationPath) :
		makedir (destinationPath)

	# Replacement in files
	for i in range (len(sources)):
		source = sources[i]
		destination = destinations[i]

		# If this is a directory
		if isdir(source):
			# Creating the destination directory
			makedir (destination)

		# If the replacement is multiline
		if multiLineReplacement:
			# Replaces in file
			multi_line_replace_in_file  (replacements, source, destination)
		else:
			# Replaces in file
			replace_in_file (replacements, source, destination)

def copy_dir(src, dst, includes, excludes = []):
	""" Copies one tree to another """
	multiFilesReplacements([], dst, src, includes, excludes)

ENCRYPTED_EXTENSION = "CIP"

def get_files_list(pattern):
	""" Get the list of files
	>>> len(get_files_list("./usef*.py")) >= 1
	True
	>>> len(get_files_list("./usef*.py;./tkfon*.py")) >= 2
	True
	>>> len(get_files_list("../application")) > 10
	True
	"""
	from os.path import isdir, isfile, split
	
	# If list of filenames detected
	if ";" in pattern:
		patterns = pattern.split(";")
	else:
		patterns = [pattern]
	result = []
	
	# For each pattern in the list
	for pattern in patterns:
		# If directory detected
		if isdir(pattern):
			# Add all files from the directory
			result += scan_all(pattern, ["*"], [])[0]
		# If file detected
		elif isfile(pattern):
			# Add the file
			result += [pattern]
		# If pattern detected
		else:
			# Split the pattern in directory and file
			directory, file = split(pattern)
			
			# Search all files
			result += scan_all(directory, [file], [])[0]
			
	# Return the list without duplicated files
	return list(set(result))

def pad(s):
	""" Pad string
	>>> len(pad(b"12"))
	16
	"""
	try:
		from Cryptodome.Cipher import AES
	except ImportError:
		from Crypto.Cipher import AES
	return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

def encrypt(content, key):
	""" Encrypt data 
	>>> ref = b"1234567890"
	>>> key = b"4"*16
	>>> enc = encrypt(ref, key)
	>>> dec = decrypt(enc, key)
	>>> dec[:len(ref)] == ref
	True
	>>> ref = "1234567890"
	>>> key = "4"*16
	>>> enc = encrypt(ref, key)
	>>> dec = decrypt(enc, key)
	>>> print(dec[:len(ref)].decode("latin-1"))
	1234567890
	"""
	try:
		from Cryptodome.Cipher import AES
		from Cryptodome        import Random
	except ImportError:
		from Crypto.Cipher import AES
		from Crypto        import Random

	if not is_python2():
		if is_string(content):
			content = content.encode("latin-1")
		if is_string(key):
			key = key.encode("latin-1")

	content = pad(content)
	iv = Random.new().read(AES.block_size)
	cipher = AES.new(key, AES.MODE_CBC, iv)
	result =  iv + cipher.encrypt(content)
	return result

def decrypt(ciphertext, key):
	""" Decrypt data
	>>> ref = b"1234567890"
	>>> key = b"4"*16
	>>> enc = encrypt(ref, key)
	>>> dec = decrypt(enc, key)
	>>> dec[:len(ref)] == ref
	True
	>>> ref = "1234567890"
	>>> key = "4"*16
	>>> enc = encrypt(ref, key)
	>>> dec = decrypt(enc, key)
	>>> print(dec[:len(ref)].decode("latin-1"))
	1234567890
	"""
	try:
		from Cryptodome.Cipher import AES
	except ImportError:
		from Crypto.Cipher import AES

	if not is_python2():
		if is_string(ciphertext):
			ciphertext = ciphertext.encode("latin-1")
		if is_string(key):
			key = key.encode("latin-1")
		
	iv = ciphertext[:AES.block_size]
	cipher = AES.new(key, AES.MODE_CBC, iv)
	plaintext = cipher.decrypt(ciphertext[AES.block_size:])
	return plaintext

def tar_list(files, display = False):
	""" Tar list of file and return the content of tar generated 
	>>> tar =tar_list(["useful.py"],True)
	Add useful.py
	>>> len(tar) >= (get_file_size("useful.py") +512)
	True"""
	from os.path import commonprefix, split, normpath, relpath
	from tarfile import open as openTar
	
	tarFile    = BytesIO()
	tarArchive = openTar(fileobj=tarFile, mode="w")
	prefix = split(normpath(commonprefix(files)))[0]
	for i in files:
		try:
			if display:
				print ("Add %s"%relpath(i,prefix))
			tarArchive.add(i,relpath(i,prefix))
		except IOError:
			print ('! Failed to add "%s"'%i)
	tarArchive.close()
	return tarFile.getvalue()

def get_time_string():
	""" Get the current time into a string 
	>>> tim = get_time_string()
	>>> len(tim)
	20
	>>> len(tim.split("__"))
	2
	>>> len(tim.split("-"))
	5
	"""
	from time     import strftime
	return strftime("%d-%m-%Y__%H-%M-%S")

def encrypt_file(files, key, output = None):
	""" Encrypt file
	>>> makedir("testunit")
	>>> r=open("testunit/Encrypt.txt","w").write("One")
	>>> import os
	>>> key    = b"O"*16
	>>> badKey = b"A"*16
	>>> filename = encrypt_file("testunit/Encrypt.txt",key,"testunit/TestEncryption.CIP")
	>>> try:
	...    decrypt_file(filename, badKey)
	... except:
	...    print("failed")
	failed
	>>> decrypt_file(filename, key)
	>>> os.remove("testunit/Encrypt.txt")
	>>> remove_dir("testunit/TestEncryption")
	"""
	from os.path import commonprefix, split, normpath, join
	if is_string(files):
		files = [files]
	content  = tar_list(files)
	cyphered = encrypt(content, key)
	if output == None:
		output   = join(split(normpath(commonprefix(files)))[0],get_time_string() + "." + ENCRYPTED_EXTENSION)
	with open(output, 'wb') as fo:
		fo.write(cyphered)
	return output

def decrypt_file(files, key):
	""" Decrypt file
	>>> makedir("testunit")
	>>> r=open("testunit/Encrypt.txt","w").write("One")
	>>> import os
	>>> key    = b"O"*16
	>>> badKey = b"A"*16
	>>> filename = encrypt_file("testunit/Encrypt.txt",key,"testunit/TestEncryption.CIP")
	>>> try:
	...    decrypt_file(filename, badKey)
	... except:
	...    print("failed")
	failed
	>>> decrypt_file(filename, key)
	>>> os.remove("testunit/Encrypt.txt")
	>>> remove_dir("testunit/TestEncryption")
	"""
	from os.path import splitext
	from os import unlink
	from tarfile import open as openTar
	
	if is_string(files):
		files = [files]

	for filename in files:
		if splitext(filename)[1][1:].upper() == ENCRYPTED_EXTENSION:
			with open(filename, 'rb') as fo:
				cyphered = fo.read()
			content = BytesIO(decrypt(cyphered, key))
			tarFilename = splitext(filename)[0]+".TAR"
			tarCopy = open(tarFilename,"wb")
			tarCopy.write(content.getvalue())
			tarCopy.close()
			with openTar(fileobj=content, mode="r") as fo:
				fo.extractall(splitext(filename)[0])
			unlink(tarFilename)
			try:
				unlink(filename)
			except:
				pass

def get_random(length = 16):
	""" Get random number
	>>> a = get_random()
	>>> b = get_random()
	>>> len(a)
	256
	>>> len(b)
	256
	>>> a == b
	False
	"""
	try:
		from Cryptodome.Cipher import AES
		from Cryptodome        import Random
	except ImportError:
		from Crypto.Cipher import AES
		from Crypto        import Random
	result = b""
	for dummy in range(length):
		result += Random.new().read(AES.block_size)
	return result

def encrypt_dir(cipFilename, key, directory, includes = ["*"], excludes = [], display=False):
	""" Encrypt directory
	>>> makedir("testunit")
	>>> import os
	>>> key    = b"O"*16
	>>> badKey = b"A"*16
	>>> encrypt_dir("testunit/cip.cip",key,"../rbtools","*.py","Color*.py",False)
	>>> try:
	...    decrypt_dir("testunit/cip.cip",badKey)
	... except:
	...    print("failed")
	failed
	>>> decrypt_dir("testunit/cip.cip",key)
	"""
	from os import remove
	zipFilename = get_directory_filename(cipFilename) + ".zip"
	zip_dir(zipFilename, directory, includes, excludes, display)
	encrypt_file(zipFilename, key, cipFilename)
	remove(zipFilename)

def decrypt_dir(cipFilename, key):
	""" Decrypt directory
	>>> makedir("testunit")
	>>> import os
	>>> key    = b"O"*16
	>>> badKey = b"A"*16
	>>> encrypt_dir("testunit/cip.cip",key,"../rbtools","*.py","Color*.py",False)
	>>> try:
	...    decrypt_dir("testunit/cip.cip",badKey)
	... except:
	...    print("failed")
	failed
	>>> decrypt_dir("testunit/cip.cip",key)
	>>> remove_dir("testunit")
	"""
	import zipfile
	from os import remove
	decrypt_file(cipFilename, key)
	zipFilename = normalize_path(get_directory_filename(cipFilename) + "\\" + get_name(cipFilename) + ".zip")
	unzip = zipfile.ZipFile(zipFilename, 'r')
	unzip.extractall(get_directory_filename(cipFilename))
	unzip.close()
	remove(zipFilename)

class KeyFile:
	def __init__(self, filename):
		from os.path import expanduser, join
		filename = join(expanduser("~"), filename)
		self.iv  = None
		self.key = None
		self.filename = filename
		try:
			self.load()
		except IOError:
			self.save()

	def load(self):
		from pickle import load
		from base64 import decodestring
		self.iv, self.key = load (open (self.filename,"rb"))
		self.iv  = decodestring(bytes(self.iv.encode("utf8")))
		self.key = decodestring(bytes(self.key.encode("utf8")))

	def save(self):
		try:
			from Cryptodome.Cipher import AES
			from Cryptodome        import Random
		except ImportError:
			from Crypto.Cipher import AES
			from Crypto        import Random
		from pickle import dump
		from base64 import encodestring
		
		if self.iv == None and self.key == None:
			self.iv  = Random.new().read(AES.block_size)
			self.key = Random.new().read(AES.block_size) + Random.new().read(AES.block_size)

		data = [encodestring(self.iv).decode('utf-8'), encodestring(self.key).decode('utf-8')]
		dump(data, open(self.filename,"wb"), protocol=2)
		print ("Created new key file '%s'"%self.filename)

	def get_password(self, password):
		try:
			from Cryptodome.Cipher import AES
		except ImportError:
			from Crypto.Cipher import AES
		if is_string(password):
			password = bytes(password.encode("utf8"))
		password = pad(password) + pad(password)
		cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
		result = cipher.encrypt(password)[0:32]
		return result

def to_hexa(data):
	""" Convert data into hexa string
	>>> print(to_hexa("1234"))
	\\x31\\x32\\x33\\x34
	>>> print(to_hexa(b"1234"))
	\\x31\\x32\\x33\\x34
	"""
	result = ""
	if is_bytes(data):
		data = data.decode("latin-1")
	for i in data:
		result += "\\x%02X"%ord(i)
	return result

def normalize_path(path):
	""" Normalize a pathname by collapsing redundant separators and up-level references """
	from os.path import normpath, sep
	result = normpath(path)
	result = result.replace("/",sep)
	result = result.replace("\\",sep)
	return adapt_path(result)

def get_file_size_string(size):
	""" Returns the file size in a string
	>>> print(get_file_size_string(123))
	123 octets
	>>> print(get_file_size_string(1234))
	1.21 Ko
	>>> print(get_file_size_string(12345))
	12.06 Ko
	>>> print(get_file_size_string(123456))
	120.56 Ko
	>>> print(get_file_size_string(1234567))
	1.18 Mo
	>>> print(get_file_size_string(12345678))
	11.77 Mo
	>>> print(get_file_size_string(123456789))
	117.74 Mo
	>>> print(get_file_size_string(1234567890))
	1.15 Go
	>>> print(get_file_size_string(12345678901234))
	11.23 To
	"""
	# Si la taille est en Go
	if size > 1073741824*1024:
		return  "%.2f To"%(size / (1073741824.*1024.))
	elif size > 1073741824:
		return  "%.2f Go"%(size / 1073741824.)
	elif size > 1048576:
		return "%.2f Mo"%(size / 1048576.)
	elif size > 1024:
		return "%.2f Ko"%(size / 1024.)
	else:
		return "%d octets"%size

def dos2unix(source, target = None):
	""" Conversion file txt Ms Dos to txt Unix"""
	lines = open(adapt_path(source),"r").readlines()
	
	if target == None:
		target = source
		
	output = open(adapt_path(target),"wb")
	for line in lines:
		line = line.replace('\x0D\x0A','\x0A')
		output.write(line)

def unix2dos(source, target = None):
	""" Converting Unix text file to text MsDos """
	lines = open(adapt_path(source),"r").readlines()
	
	if target == None:
		target = source

	output = open(adapt_path(target),"wb")
	for line in lines:
		output.write(line[:-1])
		output.write("\x0D")
		output.write("\x0A")

def import_module(filename):
	""" Import python filename 
	>>> mod = import_module("./useful.py")
	>>> mod.import_module.__name__
	'import_module'
	"""
	from os.path import abspath, split, splitext
	from sys import path
	if is_python2():
		from imp import  reload
	else:
		from importlib import reload
	
	filename = adapt_path(filename)
	modulePath = abspath(split(filename)[0])
	moduleName = splitext(split(filename)[1])[0]
	
	if not modulePath in path:
		path.append (modulePath)
	module = __import__(moduleName)
	reload (module)
	return module

def dump (data, file = None, dumpLength = 16):
	""" dump a data data in hexadecimal 
	data : string which contents the data data
	file : output file
	dumpLength : number of byte of the data per line
	>>> print(dump("\x01\x02abd"))
	00000000   01 02 61 62 64                                    |..abd           |
	<BLANKLINE>
	>>> print(dump(b"\x01\x02abd"))
	00000000   01 02 61 62 64                                    |..abd           |
	<BLANKLINE>
	"""
	if is_bytes(data):
		data = data.decode("latin-1")
	# If no defined file
	if file == None:
		file = StringIO()
	
	for j in range (0, len (data), dumpLength):
		file.write('%08X   ' % to_integer(j))
		dump_line (data [j:j + dumpLength], file, dumpLength)
		file.write('\n')

	# If a string can be returned
	if type (file) == type (StringIO()):
		return file.getvalue()
	else:
		return None

def dump_line (data, file = None, dumpLength = 0):
	""" dump a data data in hexadecimal on one line 
	>>> print(dump_line("\x01\x02abd"))
	01 02 61 62 64   |..abd|
	>>> print(dump_line(b"\x01\x02abd"))
	01 02 61 62 64   |..abd|
	"""
	if is_bytes(data):
		data = data.decode("latin-1")
	size = len(data)
	fill = 0
	
	# If no defined file
	if file == None:
		file = StringIO()
	
	# Calculation of the filling length
	if dumpLength > size:
		fill = dumpLength-size

	# Displaying values in hex
	for i in data:
		file.write('%02X ' % to_integer(i))
		
	# Filling of vacuum according to the size of the dump
	file.write('   '*fill)
	
	# Display of ASCII codes
	file.write('  |')
	
	for i in data:
		if to_integer(i) >= 0x20 and  to_integer(i) <= 0x7F : 
			file.write(i)
		else:
			file.write('.')

	# Filling of vacuum according to the size of the dump
	file.write(' '*fill)
	
	# End of data ascii
	file.write('|')
	
	# If a string can be returned
	if type (file) == type (StringIO()):
		return file.getvalue()
	else:
		return None

class Structure:
	""" Class defining a data structure
	A data structure is defined by a list of tuple,
	each type contains the type, field name, quantity and
	the default.

	The types are (same as the module struct) : 
		"pad"
		"char"
		"unsigned char"
		"short"
		"unsigned short"
		"int"
		"unsigned int"
		"long"
		"unsigned long"
		"long long"
		"unsigned long long"
		"float"
		"double"
		"char[]"
		"string"
		"void *"

	Example C following structure :
	struct Adresse
	{
		char           nom[10];
		char           prenom[10];
		char           rue[10];
		unsigned long  code_postal;
		char           ville[10];
	};

	Is converted to :
		Adresse = [
			("string",       "nom",        10, "remi"),
			("string",       "prenom",     10, "BERTHOLET"),
			("string",       "rue",        10, "53 rue ..."),
			("unsigned long","code_postal", 1, 07500),
			("string",       "ville",      10, "GUILHERAND"),
		]

	"""
	byteOrder = {
		"default"       : "@",
		"packed"        : "=",
		"little-endian" : "<",
		"big-endian"    : ">",
		"network"       : "!",
	}
	
	format = {
		"pad"                 : "x",
		"char[]"              : "s",
		"bool"                : "?",
		"char"                : "c", "unsigned char"       : "B",
		"short"               : "h", "unsigned short"      : "H",
		"int"                 : "i", "unsigned int"        : "I",
		"long"                : "l", "unsigned long"       : "L",
		"long long"           : "q", "unsigned long long"  : "Q",
		"float"               : "f",
		"double"              : "d",
		"string"              : "s",
		"void *"              : "P",
	}
	TYPE = 0
	NAME = 1
	SIZE = 2
	VALUE = 3
	
	def __init__ (self, structref, byteOrder = "default"):
		""" Building a new structure 
		>>> Adresse = [\
		("string",       "nom",        10, "Tom"),\
		("string",       "prenom",     10, "Cretinus"),\
		("string",       "rue",        10, "25 rue Hugo"),\
		("string",       "ville",      10, "PARIS"),\
		("unsigned long","code_postal"),]
		>>> adresse = Structure (Adresse)
		>>> adresse
		nom             = Tom
		prenom          = Cretinus
		rue             = 25 rue Hugo
		ville           = PARIS
		code_postal     = 0, 0x0
		<BLANKLINE>
		>>> res = dump(adresse.pack ())
		>>> "00000000   54 6F 6D 00 00 00 00 00 00 00 43 72 65 74 69 6E   |Tom.......Cretin|" in res
		True
		>>> "00000010   75 73 00 00 32 35 20 72 75 65 20 48 75 67 50 41   |us..25 rue HugPA|" in res
		True
		>>> "00000020   52 49 53 00 00 00 00 00 00 00 00 00" in res
		True
		>>> adresse.nom         = "toto"
		>>> adresse.prenom      = "alain"
		>>> adresse.rue         = "4 rue du parc"
		>>> adresse.code_postal = 26000
		>>> adresse.ville       = "VALENCE"
		>>> adresse
		nom             = toto
		prenom          = alain
		rue             = 4 rue du parc
		ville           = VALENCE
		code_postal     = 26000, 0x6590
		<BLANKLINE>
		>>> res = dump(adresse.pack ())
		>>> "00000000   74 6F 74 6F 00 00 00 00 00 00 61 6C 61 69 6E 00   |toto......alain.|" in res
		True
		>>> "00000010   00 00 00 00 34 20 72 75 65 20 64 75 20 70 56 41   |....4 rue du pVA|" in res
		True
		>>> "00000020   4C 45 4E 43 45 00 00 00 90 65 00" in res
		True
		>>> adresse.nom         = "tototititu"
		>>> adresse.prenom      = "alaindeloi"
		>>> adresse.rue         = "4 rue du parc"
		>>> adresse.code_postal = 26000
		>>> adresse.ville       = "VALENCECEC"
		>>> ad2 = Structure(Adresse)
		>>> ad2.unpack(adresse.pack())
		>>> print(ad2)
		nom             = tototititu
		prenom          = alaindeloi
		rue             = 4 rue du p
		ville           = VALENCECEC
		code_postal     = 26000, 0x6590
		<BLANKLINE>
		"""
		self.__dict__["structref"] = structref
		self.__dict__["struct"] = self.byteOrder [byteOrder]
		
		# Built structure used by the struct module
		for i in self.structref:
			try:
				size = i[self.SIZE]
			except IndexError:
				size = 1
				
			if size in (1, None):
				self.struct = self.struct + self.format [i[self.TYPE]]
			else:
				self.struct = self.struct + "%d"%size + self.format [i[self.TYPE]]
				
		# Built structure values
		self.__dict__["value"] = {}
		for i in self.structref:
			try:
				self.value[i[self.NAME]] = i[self.VALUE]
			except IndexError:
				if i[self.TYPE] in ("char[]", "string"):
					self.value[i[self.NAME]] = "\0"
				else:
					self.value[i[self.NAME]] = 0

	def __getattr__ (self, name):
		""" Get the attributes or values of fields in the structure """
		try:
			return self.__dict__[name]
		except KeyError:
			return self.__dict__["value"][name]

	def __setattr__ (self, name, value):
		""" Set the attributes or values of fields in the structure """
		try:
			self.__dict__[name] # Do not delete this line (it verifies the existence of an attribute)
			# Positioning of the existing attribute
			self.__dict__[name] = value
		except KeyError:
			# The attribute does not exist is probably value of the structure
			self.__dict__["value"][name] = value

	def size (self):
		""" Number of bytes of the structure """
		import struct
		return struct.calcsize (self.struct)

	def pack (self, encoding="utf8"):
		""" Encode a buffer from structure """
		import struct
		values = []
		
		# Build the list of values
		for i in self.structref:
			value = self.value [i[self.NAME]]
			if is_string(value):
				value = value.encode(encoding)
			values.append (value)
		return struct.pack (str(self.struct), *values)

	def unpack (self, buffer):
		""" Decoder buffer and build a structure """
		import struct
		values = struct.unpack (self.struct, buffer)
		j = 0
		for i in self.structref:
			self.value[i[self.NAME]] = values[j]
			j = j + 1

	def read (self, file):
		""" Read structure from a file """
		self.unpack (file.read (self.size()))

	def write (self, file):
		""" Write the structure in a file """
		file.write (self.pack ())

	def __repr__ (self):
		""" Convert to view the structure """
		Str = ""
		for i in self.structref:
			Str = Str + "%-15s = "%(i[self.NAME])
			value = self.value [i[self.NAME]]
			if is_integer(value):
				Str = Str + "%d, 0x%X"%(value,value)
				if value >= 0x20 and value <= 0xFF:
					Str = Str + " '" + chr (value) + "'"
			else:
				if type(value) == type(bytes(0)):
					Str = Str + value.decode("utf8","ignore")
				else:
					Str = Str + str(value) 
					
			Str = Str + "\n"
		return Str

	def __str__(self):
		return repr(self)

class Data:
	""" Abstract class containing information that will be placed in the tree """
	def __init__(self, name = "", state=None):
		self.name        = name
		self.state       = state

	def __str__(self):
		result = "'%s'"%self.name
		if self.state != None:
			result += ",%s"%self.state
		return result

	def __repr__(self):
		return str(result)

	def path(self):
		""" Preview the members making up the path """
		if '/' in self.name:
			return self.name.split("/")
		else:
			return self.name.split("\\")

class Node:
	""" Class node of a tree """
	def __init__(self, parent = None, name = None):
		self.parent = parent
		self.soon = []
		self.name = name
		self.data = None

	def set_data(self, data):
		self.data = data
		
	def get_data(self):
		return self.data

	def __repr__(self):
		return "'%s':%s"%(self.name,self.data)

	def get_soon(self, soonName):
		""" Search a son node by name """
		for name, node in self.soon:
			if name == soonName:
				return node
		return None

	def set_soon(self, name, node):
		""" Adds a node son """
		self.soon.append([name,node])
		return node

	def have_soon(self):
		if len(self.soon) > 0:
			return 1
		return 0

class Tree:
	""" Creating a tree from a list
	>>> files = [
	...   Data(r"0/01"),
	...   Data(r"0/00"),
	...   Data(r"0/06"),
	...   Data(r"0/01/001/0001/00002"),
	...   Data(r"0/01/001/0001/00001"),
	...   Data(r"0/01/001/0001/00003"),
	...   Data(r"0/01/002")]

	>>> tree = Tree ()

	>>> tree.build(files)

	>>> print (tree, end="")
	'0':None
	  '01':'0/01'
	    '001':None
	      '0001':None
	        '00002':'0/01/001/0001/00002'
	        '00001':'0/01/001/0001/00001'
	        '00003':'0/01/001/0001/00003'
	    '002':'0/01/002'
	  '00':'0/00'
	  '06':'0/06'"""
	def __init__(self, node_class = Node, root = None):
		""" Constructeur """
		if is_list(node_class):
			self.node_class = Node
			self.tree = self.node_class(parent = root)
			self.build(node_class)
		else:
			self.node_class = node_class

			# Delete the file tree
			self.tree = self.node_class(parent = root)

	def add_node(self, parent, names, data, level = 0):
		""" Adds a node to the tree of files """
		# Gets the names composing the path
		try:
			# Gets the name of the current node
			name = names[0]
			
			# Search a given node
			current = parent.get_soon(name)
			
			# If the name of the current node already exists
			if parent.get_soon(name) == None:
				# adds a new node
				current = parent.set_soon(name, self.node_class(parent = parent, name = name))
			
			# Browse by node
			self.add_node(current, names[1:], data, level + 1)
		except:
			# There are no more sub node, store the information of node
			parent.set_data(data)

	def build(self, datas):
		""" Constructs a tree of files and directories """
		# Browse the list of files
		for data in datas:
			if is_string(data):
				data = Data(data)
			elif is_list(data):
				state = None
				name = ""
				if len(data) >= 1:
					name = data[0]
				if len(data) >= 2:
					state = data[1]
				data = Data(name, state)
			# Cut the path of the file folder and piece
			self.add_node(self.tree,data.path(),data)

	def search_node(self, names):
		if type(names) == type(""):
			if '/' in names:
				names = names.split("/")
			else:
				names = names.split("\\")
		
		node = self.tree.get_soon(names[0])
		for name in names[1:]:
			node = node.get_soon(name)
		return node

	def display(self, tree, level = 0):
		""" Displays the contents of the tree """
		result = ""
		for name, node in tree.soon:
			result += "  "*level+repr(node)+"\n"
			result += self.display(tree.get_soon(name),level + 1)
		return result
	
	def __repr__ (self):
		return self.display (self.tree)

def uu_encode(binData, width = 64):
	""" uu encoding
	>>> print(uu_encode(b"12345678"))
	MTIzNDU2Nzg=
	>>> print(uu_encode("12345678"))
	MTIzNDU2Nzg=
	"""
	if is_python2():
		from base64 import encodestring 
	else:
		from base64 import encodebytes as encodestring 

	if is_python3():
		if is_string(binData):
			binData = binData.encode()
	result = ""
	uuContent = encodestring(binData).decode('utf-8').replace("\n","")
	part = uuContent[:width]
	while len(part) > 0:
		part = uuContent[:width]
		uuContent = uuContent[width:]
		result += part + "\n"
	return result.strip()

def setup_module(directory, moduleName, appendFile = None, includes = ["*.py"], excludes = []):
	""" This function is used to create an unique python script with a content of 
	directory with many python files """
	moduleHeader = '''#!/usr/bin/python
# coding:utf-8
# %(date)s

#  ____  ____  _    _  _      ____  ____  ____  _____  _   _   ___   _    ____  _____ 
# | __ \| ___|| \  / || |    | __ \| ___|| __ \|_   _|| |_| | / _ \ | |  | ___||_   _|
# |    /| __| |  \/  || |    | __ <| __| |    /  | |  |  _  |( |_| )| |_ | __|   | |  
# |_|\_\|____||_|\/|_||_|    |____/|____||_|\_\  |_|  |_| |_| \___/ |___||____|  |_|  

from sys import path
from os import remove

# Uudecode zipped module and write zip module
try:
	from base64 import decodebytes as decodestring 
except:
	from base64 import decodestring 
open("%(moduleName)s.zip","wb").write(decodestring(b"""
%(moduleContent)s
"""))

# Add zip archive module to PYTHONPATH
path.insert(0, '%(moduleName)s.zip')

# Add zip internal directory into PYTHONPATH to more easily import scripts between them
path.insert(0, '%(moduleName)s.zip/%(moduleName)s_lib')

# Import zip module
from %(moduleName)s_lib import *

# Remove zip module file : It is no longer useful
remove ("%(moduleName)s.zip")
'''
	from re import split as splitre, DOTALL
	
	moduleFilename = moduleName + ".py"
	moduleContent = BytesIO()
	date = get_time_string()

	zip_dir(moduleContent, directory, includes, excludes + [moduleFilename], False, [[moduleName, moduleName+"_lib"]])
	
	# Uuencode zipped module 
	moduleContent = uu_encode(moduleContent.getvalue(), 8192)
	
	# Write python module
	output = open(moduleFilename, "w")
	output.write(moduleHeader%locals())
	
	if appendFile != None:
		if is_string(appendFile):
			appendFile = [appendFile]
		for file in appendFile:
			content = open(file,"r").read()
			spl = splitre(r".*#<<<<(.*)#>>>>.*", content, flags=DOTALL)
			if len(spl) > 1:
				content = spl[1]
			output.write(content)
	
	print ("Module %s.py created"%moduleName)
	return moduleFilename

def thread(core):
	import threading
	threading.Thread(target = core).start()

def compute_hash(string):
	""" Compute hash 
	>>> print(compute_hash("1234"))
	49307
	>>> print(compute_hash(b"1234"))
	49307
	"""
	if is_bytes(string):
		string = string.decode("latin-1")
	hash_ = 63689
	for char in string:
		hash_ = hash_ * 378551 + ord(char)
	return hash_ % 65536


def grep(directory, include, findwhat, recursive=True, ignorecase=False, regexp=False, display=None, reversed=False):
	""" Search info in the tree 
	directory : directory where is the files to parse
	include   : list of file extensions
	findwhat  : is the string to search
	recursive : True indicates that the search is executed also in the under directory
	ignorecase : True indicates that the compare ignore case
	regex      : True indicates that the 'findwhat' is a regular expression
	display    : True indicates that the result is displayed
	reversed   : True indicates that the result is inversed (file without value displayed)
	return the list of (filename, line, line content) 
	>>> res= grep(".","useful.py","barbatruc")
	>>> file, line, content = res[0]
	>>> print("%s:%s"%(file[2:],content[10:]))
	useful.py:rep(".","useful.py","barbatruc")
	"""
	from os import walk
	from os.path import join
	from fnmatch import fnmatchcase
	from io import open
	
	def __search(findwhat, content, ignorecase, regexp):
		""" Search in content string """
		from re import search, IGNORECASE
		if regexp:
			if ignorecase:
				flag = IGNORECASE
			else:
				flag = 0
			if search(findwhat, content, flag):
				return True
		else:
			if ignorecase:
				content  = content.lower()
				findwhat = findwhat.lower()
				
			if content.find(findwhat) != -1:
				return True
		return False

	def __grep(findwhat, filename, ignorecase, regexp):
		""" Grep string in filename """
		result = []
		try:
			encoding = "utf8"
			content = open(filename,"r", encoding=encoding).read()
		except FileNotFoundError:
			return result
		except UnicodeDecodeError:
			encoding = "latin-1"
			content = open(filename,"r", encoding=encoding).read()
			
		if __search(findwhat, content, ignorecase, regexp):
			lines = open(filename,"r", encoding=encoding).readlines()
			lineNumber = 1
			for line in lines:
				if __search(findwhat, line, ignorecase, regexp):
					result.append((filename, lineNumber, line.strip()))
				lineNumber += 1
		return result

	result = []
	filesPatterns = include.split(";")
	for dirpath, dummy, filenames in walk(directory):
		for filename in filenames:
			for filePattern in filesPatterns:
				if recursive or (recursive == False and dirpath == directory):
					if fnmatchcase(filename, filePattern):
						filename = join(dirpath,filename)
						founds = __grep(findwhat, filename, ignorecase, regexp)
						result += founds
						if display != None:
							if reversed == False:
								for filename, line, content in founds:
									if type(display) == type(True):
										if display:
											print("%s:%d:%s"%(filename, line, content))
									else:
										display(filename, line, content)
							else:
								if founds == []:
									if type(display) == type(True):
										if display:
											print("%s:0:not found"%(filename, line, content))
									else:
										display(filename, 0, "not found")
									
	return result

def useful_test_clean_up():
	""">>> remove_dir("testunit")
	"""

if __name__ == "__main__":
	import doctest
	doctest.testmod()
