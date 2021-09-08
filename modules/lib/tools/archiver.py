# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Archiver files functions """
from tools import useful

HEADER_FILE=b"## PYCAMERESP ##\r\n"
def exportFiles(exportFilename, path="./config",pattern="*.json", recursive=False):
	""" Exports many file into only one file """
	result = True

	print("Export %s"%exportFilename)
	useful.remove(exportFilename)

	# Scan directory with pattern
	dirs, files = useful.scandir(path=path, pattern=pattern, recursive=recursive)
	
	try:
		# Open out file
		out = open(exportFilename,"wb")
 
		# Write type of file
		out.write(HEADER_FILE)

		# For all files found
		for filename in files:
			# All files except .tmp and sdcard
			if filename[-4:] != ".tmp" and filename[:4] != "/sd/" and filename[5:] != "./sd/":
				# Write file header
				size = useful.filesize(filename)
				out.write(b"# %d:%s\r\n"%(size, useful.tobytes(filename)))

				print("  Export '%s' size=%d"%(filename, size))
				try:
					# Write file
					content = open(filename,"rb")
					while size > 0:
						data = content.read(2048)
						out.write(data)
						size -= len(data)

					# Write end of file
					out.write(b"\r\n\r\n")
				except Exception as err:
					useful.syslog(err)
					result = False
					break
				finally:
					content.close()
	except Exception as err:
		useful.syslog(err)
		result = False
	finally:
		print("Export %s"%("success" if result else "failed"))
		out.close()
	return result

def importFiles(importFilename, simulated=False):
	""" Import files and write all files """
	result = True
	print("Import %s"%importFilename)
	try:
		readSize = useful.filesize(importFilename)
		imported = open(importFilename,"rb")
		if not useful.ismicropython():
			simulated = True

		# Read the type of file
		if imported.read(len(HEADER_FILE)) != HEADER_FILE:
			result = False
		else:
			while imported.tell() < readSize:
				# Read the start of file
				comment = imported.read(2)
				if comment != b"# ":
					result = False
					break

				# Read the file size
				size = b""
				while True:
					char = imported.read(1)
					if char == b":":
						break
					elif not char in b"0123456789":
						result = False
						break
					size += char
				if result == False:
					break
				size = eval(size)

				# Read filename
				filename = b""
				while True:
					char = imported.read(1)
					if char == b"\r":
						break
					filename += char
				filename = useful.tostrings(filename)
				char = imported.read(1)
				if char != b"\n":
					result = False
					break

				# Read the file
				print("  Import '%s' size=%d"%(filename, size))
				
				try:
					if simulated == False:
						content = open(filename,"wb")
					while size > 0:
						data = imported.read(size if size < 2048 else 2048)
						if simulated == False:
							content.write(data)
						size -= len(data)
				except Exception as err:
					useful.syslog(err)
					result = False
				finally:
					if simulated == False:
						content.close()
				
				# Read the end of file
				if imported.read(4) != b"\r\n\r\n":
					result = False
					break
	except Exception as err:
		useful.syslog(err)
		result = False
	finally:
		print("Import %s"%("success" if result else "failed"))
		imported.close()
	useful.remove(importFilename)
	return result
