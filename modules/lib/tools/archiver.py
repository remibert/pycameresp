# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Archiver files functions """
from tools import logger,filesystem,exchange

def download_files(download_filename, path="./config",pattern="*.json", recursive=False):
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
			# All files except .tmp and sdcard
			if filename[-4:] != ".tmp" and filename[:4] != "/sd/" and filename[5:] != "./sd/":
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
