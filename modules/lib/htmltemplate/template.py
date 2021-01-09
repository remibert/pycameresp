# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Base class of html templates """
from tools import useful
from tools.useful import log

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
			self.addChildren(children)

	def addChildren(self, children):
		""" Add children of html template in the current instance """
		if type(children) == type([]) or type(children) == type((0,)):
			for child in children:
				self.addChildren(child)
		else:
			self.children.append(children)

	async def write(self, file):
		""" Write to the file stream the html template (parse also all children) """
		try:
			await file.write(self.getBegin(self))
			for child in self.children:
				if isinstance(child, Template):
					await child.write(file)
				elif child != None:
					if type(child) == type(b""):
						await file.write(child)
					elif type(child) == type([]) or type(child) == type((0,)):
						for item in child:
							if item != None:
								await item.write(file)
			await file.write(self.getEnd(self))
		except Exception as err:
			await file.write(useful.htmlException(err))
