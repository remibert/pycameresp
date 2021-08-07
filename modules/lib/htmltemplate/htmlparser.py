# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET 
""" This script parse the template.html file and creates the template classes 
that can be used to compose a web page.
This automatically creates the content of file lib/htmltemplate/htmlclasses.py """
import re

def findall(pattern, text):
	""" Finds the %(xxx)s fields in the line """
	spl = re.compile(pattern).split(text)
	result = []
	beginTag = ""
	endTag   = None
	beginFormat = ""
	endFormat = ""
	initText = text
	for s in spl:
		text = text[len(s)+2:]
		end = text.find(")s")
		var = ""
		if len(text) > 0:
			var = text[:end]
			result.append(var)
		if var == "content":
			beginTag += s
			endTag = ""
		elif endTag != None:
			endTag += s
			if var != "":
				if var in ["disabled","checked","active","selected"]:
					endFormat += " b'%s' if self.%s else b'',"%(var, var)
				else:
					endFormat += "self.%s,"%var
				endTag += "\x25s"
		else:
			beginTag += s
			if var != "":
				if var in ["disabled","checked","active","selected"]:
					beginFormat += " b'%s' if self.%s else b'',"%(var, var)
				else:
					beginFormat += "self.%s,"%var
				beginTag += "\x25s"
		text = text[end+2:]
	if endTag == None:
		endTag = ""
		endFormat = ""
	return result, beginTag, endTag, beginFormat, endFormat

def parse(force=False):
	""" Parse the www/template.html and createsthe content of file lib/htmltemplate/htmlclasses.py """
	from htmltemplate import WWW_DIR, TEMPLATE_FILE, TEMPLATE_PY
	# pylint: disable=duplicate-string-formatting-argument
	print("Parse html template")
	lines = open(WWW_DIR+TEMPLATE_FILE).readlines()
	pyClassFile = open(TEMPLATE_PY,"w")
	pyClassFile.write("''' File automatically generated with template.html content '''\nfrom htmltemplate.template import Template \n")
	stack = []
	for line in lines:
		if "<!--" in line:
			spl = line.split("<!--")
			if ":begin-->" in line:
				classname = spl[1].split(":begin-->")[0]
				stack.append([classname,"",""])
			elif ":end-->" in line:
				classname = spl[1].split(":end-->")[0]
				if classname != stack[-1][0]:
					raise SyntaxError()
				classname, text, comment = stack.pop()
				attributes, beginTag, endTag, beginFormat, endFormat = findall(r'\%\([A-Za-z_0-9]*\)s',text)

				print("Html template update %s"%classname)
				classattributes = set()
				for attribute in attributes:
					classattributes.add(attribute)

				comment = comment.rstrip()

				pyClassFile.write("""\n%s\n"""%comment)

				if beginTag != "":
					pyClassFile.write("""begTag%s = b'''%s'''\n"""%(classname,beginTag))
				if endTag != "":
					pyClassFile.write("""endTag%s = b'''%s'''\n"""%(classname,endTag))
				pyClassFile.write("""def %s(*args, **params):\n"""%classname)

				pyClassFile.write("""\tself = Template(*(("%s",) + args), **params)\n\n"""%classname)

				pyClassFile.write("""\tdef getBegin(self):\n""")
				if beginFormat == "":
					if beginTag != "":
						pyClassFile.write("""\t\tglobal begTag%s\n"""%classname)
						pyClassFile.write("""\t\treturn begTag%s\n"""%(classname))
					else:
						pyClassFile.write("""\t\treturn b''\n""")
				else:
					pyClassFile.write("""\t\tglobal begTag%s\n"""%classname)
					pyClassFile.write("""\t\treturn begTag%s%s(%s)\n"""%(classname, "\x25",beginFormat[:-1]))
				pyClassFile.write("""\tself.getBegin     = getBegin\n\n""")

				pyClassFile.write("""\tdef getEnd(self):\n""")
				if endFormat == "":
					if endTag != "":
						pyClassFile.write("""\t\tglobal endTag%s\n"""%classname)
						pyClassFile.write("""\t\treturn endTag%s\n"""%(classname))
					else:
						pyClassFile.write("""\t\treturn b''\n""")
				else:
					pyClassFile.write("""\t\tglobal endTag%s\n"""%classname)
					pyClassFile.write("""\t\treturn endTag%s%s(%s)\n"""%(classname, "\x25", endFormat[:-1]))
				pyClassFile.write("""\tself.getEnd       = getEnd\n\n""")

				for attribute in classattributes:
					if attribute in ["pattern"]:
						pyClassFile.write('\tself.{:<12} = params.get("{}", b"*")\n'.format(attribute,attribute))
					elif attribute in ["id","name"]:
						pyClassFile.write('\tself.{:<12} = params.get("{}", b"%d"%id(self))\n'.format(attribute,attribute))
					elif attribute in ["disabled","active"]:
						pyClassFile.write('\tself.{:<12} = params.get("{}", False)\n'.format(attribute,attribute))
					elif attribute in ["checked"]:
						pyClassFile.write('\tself.{:<12} = params.get("{}", True)\n'.format(attribute,attribute))
					else:
						pyClassFile.write('\tself.{:<12} = params.get("{}", b"")\n'.format(attribute,attribute))
				pyClassFile.write('\treturn self\n')
			else:
				raise SyntaxError()
		else:
			if line.strip() != "":
				if len(stack) >= 1:
					stack[-1][1] += line.strip()
					stack[-1][2] += "# " +line.lstrip()

	pyClassFile.close()
