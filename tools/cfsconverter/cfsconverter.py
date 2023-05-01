#!/usr/bin/python3
# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Allows you to convert a CFS file to a ZIP file and vice versa """
import tempfile
import sys
import os.path
import os
import time
from zipfile import ZipFile, ZIP_DEFLATED
sys.path.append("../../modules/lib")
# pylint:disable=consider-using-enumerate
# pylint:disable=wrong-import-position
# pylint:disable=import-error
# pylint:disable=consider-using-f-string
# pylint:disable=unspecified-encoding
from tools.exchange import FileReader, FileWriter

def printing(data, end=""):
	""" Printing function """
	print(data,end)

def cfs2zip(cfs_filename, printer=printing):
	""" Converted a pycameresp file to a zip file """
	zip_filename = "%s.zip"%os.path.splitext(cfs_filename)[0]
	with ZipFile(zip_filename,"w", ZIP_DEFLATED) as zip_file:
		printer("Convert to zip %s"%zip_filename)
		with open(cfs_filename,"rb") as cfs_file:
			with tempfile.TemporaryDirectory() as tempdir:
				read_size = os.path.getsize(cfs_filename)
				while cfs_file.tell() < read_size:
					file_reader = FileReader()
					if file_reader.read(tempdir, cfs_file):
						printer("  Add '%s'"%file_reader.filename.get())
						tmp_filename = os.path.join(tempdir, file_reader.filename.data.decode("utf8"))
						zip_file.write(tmp_filename, file_reader.filename.get())
					else:
						break


def zip2cfs(zip_filename, printer=printing):
	""" Converted a zip file to a pycameresp file """
	file_writer = FileWriter()
	with ZipFile(zip_filename,"r") as zip_file:
		cfs_filename = "%s.cfs"%os.path.splitext(zip_filename)[0]
		with open(cfs_filename, "wb") as cfs_writer:
			printer("Convert to cfs %s"%cfs_filename)
			for file in zip_file.infolist():
				if file.is_dir() is False:
					zip_content = tempfile.NamedTemporaryFile(delete=False)
					zip_content.write(zip_file.read(file.filename))
					zip_content.close()
					file_time = file.date_time + (0,0,0)
					t = int(time.mktime(file_time))
					os.utime(zip_content.name, (t,t))
					try:
						printer("  Add '%s'"%file.filename)
						file_writer.write(zip_content.name, None, cfs_writer, file.filename, None)
					finally:
						os.unlink(zip_content.name)

def cfsconverter(filename):
	""" Convert a CFS file to a ZIP file and vice versa """
	if os.path.splitext(filename)[1].lower() == ".cfs":
		cfs2zip(filename)
	elif os.path.splitext(filename)[1].lower() == ".zip":
		zip2cfs(filename)
	else:
		print("File '%s' not supported"%filename)

if __name__ == "__main__":
	if len(sys.argv) == 2:
		cfsconverter(sys.argv[1])
	else:
		print("Allows you to convert a CFS file to a ZIP file and vice versa\ncfsconverter.py [filename]")
	# cfs2zip("/Users/remi/Downloads/test.config.cfs")
	# zip2cfs("/Users/remi/Downloads/test.config2.zip")
