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
#~ print(lib_path)
sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/../../modules/lib"))
# pylint:disable=consider-using-enumerate
# pylint:disable=wrong-import-position
# pylint:disable=import-error
# pylint:disable=consider-using-f-string
# pylint:disable=unspecified-encoding
from tools.exchange import FileReader, FileWriter

def printing(data, end=""):
	""" Printing function """
	print(data,end)

def cfs2zip(cfs_filename, zip_filename=None, printer=printing):
	""" Converted a pycameresp file to a zip file """
	if zip_filename is None:
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

def makedir(directory):
	""" Make directory recursively """
	directories = [directory]
	while 1:
		parts = os.path.split(directory)
		if parts[1] == "" or parts[0] == "":
			break
		directories.append(parts[0])
		directory = parts[0]

	directories.reverse()
	for d in directories:
		if not(os.path.exists(d)):
			os.mkdir(d)

def cfs2dir(cfs_filename, directory=None, printer=printing):
	""" Converted a pycameresp file to a zip file """
	if directory is None:
		directory = "%s"%os.path.splitext(cfs_filename)[0]
	elif not os.path.isabs(directory):
		directory = os.path.join(os.path.split(os.path.realpath(cfs_filename))[0], directory)
	printer("Extract '%s' into '%s'"%(cfs_filename, directory))
	makedir(directory)
	with open(cfs_filename,"rb") as cfs_file:
		read_size = os.path.getsize(cfs_filename)
		while cfs_file.tell() < read_size:
			file_reader = FileReader()
			if file_reader.read(directory, cfs_file):
				printer("  Extract '%s'"%file_reader.filename.get())
			else:
				break

def zip2cfs(zip_filename, cfs_filename=None, printer=printing):
	""" Converted a zip file to a pycameresp file """
	file_writer = FileWriter()
	with ZipFile(zip_filename,"r") as zip_file:
		if cfs_filename is None:
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

def main():
	import argparse
	parser = argparse.ArgumentParser(description="Convert CFS file into ZIP, or ZIP into CFS file")
	parser.add_argument("-x", "--extract",  help="extract all files",            action="store_true")
	parser.add_argument("-o", "--output",   help="output filename or directory", type=str, default=None)
	parser.add_argument("filename",         help="CFS or zip filename",          type=str)
	args = parser.parse_args()
	if len(sys.argv) == 1:
		parser.print_help()
	else:
		
		if os.path.splitext(args.filename)[1].lower() == ".cfs":
			if args.extract:
				cfs2dir(args.filename, args.output)
			else:
				cfs2zip(args.filename, args.output)
		elif os.path.splitext(args.filename)[1].lower() == ".zip":
			zip2cfs(args.filename, args.output)
		else:
			print("File '%s' not supported"%args.filename)

if __name__ == "__main__":
	main()
