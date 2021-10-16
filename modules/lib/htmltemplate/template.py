# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Base class of html templates """
from tools import useful

class Template:
	""" Base class of html templates """
	def __init__(self, classname, *args, **params):
		self.classname = classname
		self.children = []
		if len(args) > 0:
			children = args[0]
		else:
			children = params.get("children",[])
		if children != []:
			self.add_children(children)

	def add_children(self, children):
		""" Add children of html template in the current instance """
		if type(children) == type([]) or type(children) == type((0,)):
			for child in children:
				self.add_children(child)
		else:
			self.children.append(children)

	async def write(self, file):
		""" Write to the file stream the html template (parse also all children) """
		try:
			# pylint: disable=no-member
			await file.write(self.get_begin(self))
			for child in self.children:
				if isinstance(child, Template):
					await child.write(file)
				elif child is not None:
					if type(child) == type(b""):
						await file.write(child)
					elif type(child) == type([]) or type(child) == type((0,)):
						for item in child:
							if item is not None:
								await item.write(file)
			await file.write(self.get_end(self))
		except Exception as err:
			await file.write(useful.html_exception(err))
