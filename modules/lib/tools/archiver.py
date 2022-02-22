# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Archiver files functions """
from tools import logger,filesystem
from tools.exchange import FileReader, FileWriter

def export_files(export_filename, path="./config",pattern="*.json", recursive=False):
	""" Exports many file into only one file """
	result = True

	logger.syslog("Export %s"%export_filename)
	filesystem.remove(export_filename)

	# Scan directory with pattern
	_, files = filesystem.scandir(path=path, pattern=pattern, recursive=recursive)

	try:
		# Open out file
		out_file = open(export_filename,"wb")

		file_write = FileWriter()
		# For all files found
		for filename in files:
			# All files except .tmp and sdcard
			if filename[-4:] != ".tmp" and filename[:4] != "/sd/" and filename[5:] != "./sd/":
				logger.syslog("  Export '%s'"%(filename))
				if file_write.write(filename, None, out_file) is False:
					result = False
					break
	except Exception as err:
		logger.syslog(err)
		result = False
	finally:
		logger.syslog("Export %s"%("success" if result else "failed"))
		out_file.close()
	return result

def import_files(import_filename, directory="/"):
	""" Import files and write all files """
	result = True
	logger.syslog("Import %s"%import_filename)
	try:
		in_file = open(import_filename,"rb")
		if filesystem.ismicropython():
			simulated = False
		else:
			simulated = True

		read_size = filesystem.filesize(import_filename)

		while in_file.tell() < read_size:
			file_reader = FileReader(simulated)
			res = file_reader.read(directory, in_file)
			logger.syslog("Import %s %s"%(file_reader.filename.get(), "" if res else "failed"))

	except Exception as err:
		logger.syslog(err)
		result = False
	finally:
		logger.syslog("Import %s"%("success" if result else "failed"))
		in_file.close()
	filesystem.remove(import_filename)
	return result
