# Distributed under MIT License
# Copyright (c) 2020 Remi BERTHOLET

def isString(data):
	""" Indicates if the data is a string
	>>> isString("str")
	True
	>>> isString(u"jjj")
	True
	>>> isString(12)
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

def adaptPath(path):
	from sys import platform  
	if platform != "win32":
		return path.replace("\\","/")
	return path

def normalizeList(lst):
	from os import sep
	result = []
	
	if isString(lst):
		lst = [lst]
	
	for item in lst:
		if sep == "/":
			tmp = item.replace("\\",sep)
		else:
			tmp = item.replace("/",sep)
		result.append(adaptPath(tmp))
	return result
	
def mustBeAdded(filename, includes, excludes):
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
	return adding

def addFilesInList(filename, includes, excludes, lst):
	if mustBeAdded(filename, includes, excludes):
		lst.append(filename)

def scanAll(root, directory, includes = ["*"], excludes = []):
	""" Parse a directory and returns the list of files and directories """
	from os import walk
	from os.path import join

	excludes = normalizeList(excludes)
	includes = normalizeList(includes)
	directory = adaptPath(directory)

	if   isString(includes)      : includes = [includes]
	elif type(includes) == type(None): includes = []
		
	if   isString(excludes)      : excludes = [excludes]
	elif type(excludes) == type(None): excludes = []
	
	files = []
	directories = []

	lengthDirectory = len(root)
	for i in walk(root + "/" + directory):
		dirpath, dirnames, filenames = i
		for dirname in dirnames:
			addFilesInList(join(dirpath[lengthDirectory+1:], dirname), includes, excludes, directories)

		for filename in filenames:
			addFilesInList(join(dirpath[lengthDirectory+1:], filename), includes, excludes, files)

	all_ = directories + files
	return all_, files, directories

class FtpSync:
	def __init__(self, host, port = 21, user="", password=""):
		self.files = {}
		self.directories = []
		self.ftp = None
		self.includes = ["*"]
		self.excludes = []
		self.host = host
		self.port = port
		self.user = user
		self.password = password
		self.connect()

	def connect(self):
		from ftplib import FTP
		self.ftp = FTP()
		self.ftp.connect(self.host, self.port)
		self.ftp.login(self.user, self.password)

	def scan(self, path="/", includes=["*"], excludes=[], recurse=False):
		self.ftp.cwd(path)
		self.path=path
		self.dirs =[]
		self.includes = includes
		self.excludes = excludes
		self.ftp.retrlines('LIST',self.parseLine)
		self.directories += self.dirs
		if recurse:
			for dirinfo in self.dirs:
				directory, year,month,day,hour,minute = dirinfo
				#~ print("Scan '%s'"%directory)
				self.scan("/"+directory, includes, excludes, recurse)

	def parseLine(self, line):
		from re import split
		from time import localtime
		
		spl = split("([\-drwx]*) *([0-9]*) *([a-z]*) *([a-z]*) *([0-9]*) *([A-Z][a-z][a-z]) *([0-9]*) *([0-9:]*) *(.*)",line)

		if len(spl) == 11:
			dummy, ugo, dummy, owner, group, size, month, day, timeyear, filename, dummy = spl
			
			if ":" in timeyear:
				year = localtime().tm_year
				hour, minute = timeyear.split(":")
				hour = int(hour)
				minute = int(minute)
			else:
				year = timeyear
				hour = 0
				minute = 0
			day = int(day)
			year = int(year)
			months = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
			month = months[month]
			size = int(size)
			if ugo[0] != "d":
				file = self.path+"/"+filename
				file = file.replace("//","/")
				#file = filename.replace("//","/").lstrip("/")
				if mustBeAdded(file, self.includes, self.excludes):
					self.files[file] = (year,month,day,hour,minute,size)
					#~ print("%04d/%02d/%02d %02d:%02d %8d %s"%(year,month,day,hour,minute,size,file))
				else:
					pass
					#~ print("%04d/%02d/%02d %02d:%02d %8d %s excluded"%(year,month,day,hour,minute,size,file))
			else:
				directory = self.path+"/"+filename
				directory = directory.replace("//","/")
				#directory = filename.replace("//","/").lstrip("/")
				if mustBeAdded(directory, self.includes, self.excludes):
					self.dirs.append((directory.lstrip("/"),year,month,day,hour,minute))
					#~ print("%04d/%02d/%02d %02d:%02d          [%s]"%(year,month,day,hour,minute,directory))
				else:
					pass
					#~ print("%04d/%02d/%02d %02d:%02d          [%s] excluded"%(year,month,day,hour,minute,directory))
		#~ else:
			#~ print("Cannot parse ftp list :'%s'"%line)
	
	def copy(self, sourceFilename, destinationFilename):
		self.ftp.storbinary("STOR %s"%destinationFilename, open(sourceFilename,"rb"))

class Filters:
	def __init__(self, includes = ["*"], excludes = ["*.pyc", ".DS_Store", "*/__pycache__/*"]):
		self.includes = includes
		self.excludes = excludes

class Source:
	def __init__(self, root=None, path=None, filters=None):
		self.root = root
		self.path = path
		self.filters = filters

class Destination:
	def __init__(self, host=None, port=21, user="", password="", path="/", filters=None):
		self.host = host
		self.port = port
		self.user = user
		self.password = password
		self.path = path
		self.filters = filters

class Synchronization:
	def __init__(self, source, destination):
		self.src = source
		self.dst = destination
		self.ftp = None
		
	def synchronize(self):
		sources      = self.scanSource()
		self.ftp = FtpSync(self.dst.host, self.dst.port, self.dst.user, self.dst.password)
		destinations = self.scanDestination()
		self.copyToDestination(sources, destinations, True)

	def scanSource(self):
		fileinfos = {}
		from os import stat, getcwd
		from time import localtime
		
		all, files, directories = scanAll(self.src.root, self.src.path, self.src.filters.includes, self.src.filters.excludes)
		
		for file in files:
			s = stat(self.src.root + "/" +file)
			date= localtime(s.st_mtime)
			fileinfos[file] = (date.tm_year, date.tm_mon, date.tm_mday, date.tm_hour, date.tm_min, s.st_size)
		return fileinfos

	def scanDestination(self):
		self.ftp.scan(self.dst.path, self.dst.filters.includes, self.dst.filters.excludes, True)
		result = self.ftp.files
		return result

	def copyToDestination(self, sources, destinations, copyfile=False):
		for source in sources.keys():
			if source in destinations:
				if sources[source][-1] != destinations[source][-1]:
					print("%-40s updated(size different)"%source)
					if copyfile:
						self.ftp.copy(self.src.root + source, source)
				else:
					comp = self.compare(sources[source], destinations[source])
					if comp == 0:
						#~ print("%-40s equal"%source)
						pass
					elif comp < 0:
						#~ print("%-40s older"%source)
						pass
					else:
						print("%-40s updated(newer)"%source)
						if copyfile:
							self.ftp.copy(self.src.root + source, source)
			else:
				print("%-40s updated(missing)"%source)
				if copyfile:
					self.ftp.copy(self.src.root + source, source)
		
		for destination in destinations:
			if not destination in sources:
				print("%-40s to delete"%destination)

	def compare(self, source, destination):
		syear, smonth, sday, shour, smin, ssize = source
		dyear, dmonth, dday, dhour, dmin, dsize = destination
		#~ print(source, destination)
		if   syear > dyear:  return 1
		elif syear < dyear: return -1
		else:
			if smonth > dmonth: return 1
			if smonth < dmonth: return -1
			else:
				if sday > dday: return 1
				if sday < dday: return -1
				else:
					if shour > dhour: return 1
					if shour < dhour: return -1
					else:
						if smin > dmin: return 1
						if smin < dmin: return -1
		return 0

if __name__ == "__main__":
	from os import getcwd

	filters     = Filters(\
		includes=["*"], 
		excludes=["ESP32","*.json",".DS_Store",".*","sync.*","*.txt","*/__pycache__/*","*/simul/*","*.pyc"])

	path = "/"
	destination = Destination(\
		host    = "192.168.1.132", 
		port    = 21, 
		user    = "", 
		password= "", 
		path    = path, 
		filters = filters)

	source      = Source(\
		root    = getcwd() + "/modules",
		path    = path,
		filters = filters)

	synchro     = Synchronization(source, destination)
	synchro.synchronize()
