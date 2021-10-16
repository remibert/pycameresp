# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function to check if the template.html is changed and the generates the htmlclasses.py """
from htmltemplate import WWW_DIR, TEMPLATE_FILE, TEMPLATE_PY

def parse(force=False):
	""" Check that the template.html file has been modified and if so rebuild the file htmlclasses.py """
	def get_modified_time(filename):
		try:
			from uos import stat
			ST_MTIME = 8
		except:
			from os import stat
			from stat import ST_MTIME
		try:
			return stat(filename)[ST_MTIME]
		except:
			return 0
	if get_modified_time(WWW_DIR+TEMPLATE_FILE) > get_modified_time(TEMPLATE_PY) or force:
		from htmltemplate import htmlparser
		htmlparser.parse(force)
	else:
		print("Html up to date")
		# from htmltemplate import htmlparser
		# htmlparser.parse(force)

if __name__ == "__main__":
	parse(True)
	from htmltemplate.htmlclasses import *
	del parse
else:
	parse()
	from htmltemplate.htmlclasses import *
	del parse
