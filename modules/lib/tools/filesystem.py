# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Miscellaneous path functions """
import os
import sys

try:
	import fnmatch
except:
	from tools import fnmatch

try:
	import uos
except:
	pass

def exists(filename):
	""" Test if the filename existing """
	try:
		_ = os.lstat(filename)
		return True
	except:
		try:
			_ = os.stat(filename)
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

def ismicropython():
	""" Indicates if the python is micropython """
	if sys.implementation.name == "micropython":
		return True
	return False

def scandir(path, pattern, recursive, displayer=None):
	""" Scan recursively a directory """
	filenames   = []
	directories = []
	if path == "":
		path = "."
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
						filenames = [""]
					else:
						filenames.append(filename)
	return directories, filenames

def prefix(files):
	""" Get the common prefix of all files """
	# Initializes counters
	counters = []

	# For all files
	for file in files:
		# Split the file name into a piece
		paths = file.split("/")

		# For each piece
		length = len(paths)
		for i in range(0,length):
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

def normpath(path):
	# Extract from https://github.com/python/cpython/blob/main/Lib/posixpath.py
	"""Normalize path, eliminating double slashes, etc."""
	# path = os.fspath(path)
	if isinstance(path, bytes):
		sep = b'/'
		empty = b''
		dot = b'.'
		dotdot = b'..'
	else:
		sep = '/'
		empty = ''
		dot = '.'
		dotdot = '..'
	if path == empty:
		return dot
	initial_slashes = path.startswith(sep)
	# POSIX allows one or two initial slashes, but treats three or more
	# as single slash.
	# (see http://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap04.html#tag_04_13)
	if (initial_slashes and
		path.startswith(sep*2) and not path.startswith(sep*3)):
		initial_slashes = 2
	comps = path.split(sep)
	new_comps = []
	for comp in comps:
		if comp in (empty, dot):
			continue
		if (comp != dotdot or (not initial_slashes and not new_comps) or
				(new_comps and new_comps[-1] == dotdot)):
			new_comps.append(comp)
		elif new_comps:
			new_comps.pop()
	comps = new_comps
	path = sep.join(comps)
	if initial_slashes:
		path = sep*initial_slashes + path
	return path or dot
