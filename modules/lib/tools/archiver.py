# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Archiver files functions """
from tools import logger,filesystem
from tools.exchange import FileReader, FileWriter

def export_files(export_filename, path="./config",pattern="*.json", recursive=False):
	""" Exports many file into only one file """
	result = True

	print("Export %s"%export_filename)
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
				print("  Export '%s'"%(filename))
				if file_write.write(filename, None, out_file) is False:
					result = False
					break
	except Exception as err:
		logger.syslog(err)
		result = False
	finally:
		print("Export %s"%("success" if result else "failed"))
		out_file.close()
	return result

def import_files(import_filename, directory="/", simulated=False):
	""" Import files and write all files """
	result = True
	print("Import %s"%import_filename)
	try:
		in_file = open(import_filename,"rb")
		if not filesystem.ismicropython():
			simulated = True

		read_size = filesystem.filesize(import_filename)
		file_reader = FileReader()
		while in_file.tell() < read_size:
			if file_reader.read(in_file) is not None:
				print("Import %s"%file_reader.filename.get())
				if filesystem.ismicropython():
					if simulated is False:
						file_reader.save(directory)
				file_reader = FileReader()

	except Exception as err:
		logger.syslog(err)
		result = False
	finally:
		print("Import %s"%("success" if result else "failed"))
		in_file.close()
	filesystem.remove(import_filename)
	return result
