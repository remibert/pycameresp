# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Archiver files functions """
from tools import logger,filesystem,exchange, fnmatch

def download_files(download_filename, path="./config", pattern="*.json", excludes=None, recursive=False):
	""" Download many file into only one file """
	result = True

	logger.syslog("Download %s"%download_filename)
	filesystem.remove(download_filename)

	# Scan directory with pattern
	_, files = filesystem.scandir(path=path, pattern=pattern, recursive=recursive)

	try:
		# Open out file
		out_file = open(download_filename,"wb")

		file_write = exchange.FileWriter()
		# For all files found
		for filename in files:
			exclude = False
			if excludes is not None:
				if type(excludes) == type(""):
					excludes = [excludes]

				if type(excludes) == type([]):
					for pattern in excludes:
						if fnmatch.fnmatch(filesystem.normpath(filename),pattern):
							exclude = True
							break

			if exclude is False:
				logger.syslog("  Download '%s'"%(filename))
				if file_write.write(filename, None, out_file) is False:
					result = False
					break
	except Exception as err:
		logger.syslog(err)
		result = False
	finally:
		logger.syslog("Download %s"%("success" if result else "failed"))
		out_file.close()
	return result

def upload_files(upload_filename, directory="/"):
	""" Upload files and write all files """
	result = True
	logger.syslog("Upload %s"%upload_filename)
	try:
		in_file = open(upload_filename,"rb")
		if filesystem.ismicropython():
			simulated = False
		else:
			simulated = True

		read_size = filesystem.filesize(upload_filename)
		while in_file.tell() < read_size:
			file_reader = exchange.FileReader(simulated)
			if filesystem.ismicropython() is False:
				directory = "/tmp"

			res = file_reader.read(directory, in_file)
			logger.syslog("  Upload %s %s"%(file_reader.filename.get(), "" if res else "failed"))

	except Exception as err:
		logger.syslog(err)
		result = False
	finally:
		logger.syslog("Upload %s"%("success" if result else "failed"))
		in_file.close()
	filesystem.remove(upload_filename)
	return result
