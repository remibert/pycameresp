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
	begin_tag = ""
	end_tag   = None
	begin_format = ""
	end_format = ""
	initText = text
	for s in spl:
		text = text[len(s)+2:]
		end = text.find(")s")
		var = ""
		if len(text) > 0:
			var = text[:end]
			result.append(var)
		if var == "content":
			begin_tag += s
			end_tag = ""
		elif end_tag is not None:
			end_tag += s
			if var != "":
				if var in ["disabled","checked","active","selected"]:
					end_format += " b'%s' if self.%s else b'',"%(var, var)
				else:
					end_format += "self.%s,"%var
				end_tag += "\x25s"
		else:
			begin_tag += s
			if var != "":
				if var in ["disabled","checked","active","selected"]:
					begin_format += " b'%s' if self.%s else b'',"%(var, var)
				else:
					begin_format += "self.%s,"%var
				begin_tag += "\x25s"
		text = text[end+2:]
	if end_tag is None:
		end_tag = ""
		end_format = ""
	return result, begin_tag, end_tag, begin_format, end_format

def parse(force=False):
	""" Parse the www/template.html and createsthe content of file lib/htmltemplate/htmlclasses.py """
	from htmltemplate import WWW_DIR, TEMPLATE_FILE, TEMPLATE_PY
	# pylint: disable=duplicate-string-formatting-argument
	print("Parse html template")
	lines = open(WWW_DIR+TEMPLATE_FILE).readlines()
	py_class_file = open(TEMPLATE_PY,"w")
	py_class_file.write("''' File automatically generated with template.html content '''\n# pylint:disable=missing-function-docstring\n# pylint:disable=trailing-whitespace\n# pylint:disable=too-many-lines\nfrom htmltemplate.template import Template \n")

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
				attributes, begin_tag, end_tag, begin_format, end_format = findall(r'\%\([A-Za-z_0-9]*\)s',text)

				print("Html template update %s"%classname)
				classattributes = set()
				for attribute in attributes:
					classattributes.add(attribute)

				comment = comment.rstrip()

				py_class_file.write("""\n%s\n"""%comment)

				if begin_tag != "":
					py_class_file.write("""beg_tag%s = b'''%s'''\n"""%(classname,begin_tag))
				if end_tag != "":
					py_class_file.write("""end_tag%s = b'''%s'''\n"""%(classname,end_tag))
				py_class_file.write("""def %s(*args, **params):\n"""%classname)

				py_class_file.write("""\tself = Template(*(("%s",) + args), **params)\n\n"""%classname)

				py_class_file.write("""\tdef get_begin(self):\n""")
				if begin_format == "":
					if begin_tag != "":
						py_class_file.write("""\t\tglobal beg_tag%s\n"""%classname)
						py_class_file.write("""\t\treturn beg_tag%s\n"""%(classname))
					else:
						py_class_file.write("""\t\treturn b''\n""")
				else:
					py_class_file.write("""\t\tglobal beg_tag%s\n"""%classname)
					py_class_file.write("""\t\treturn beg_tag%s%s(%s)\n"""%(classname, "\x25",begin_format[:-1]))
				py_class_file.write("""\tself.get_begin     = get_begin\n\n""")

				py_class_file.write("""\tdef get_end(self):\n""")
				if end_format == "":
					if end_tag != "":
						py_class_file.write("""\t\tglobal end_tag%s\n"""%classname)
						py_class_file.write("""\t\treturn end_tag%s\n"""%(classname))
					else:
						py_class_file.write("""\t\treturn b''\n""")
				else:
					py_class_file.write("""\t\tglobal end_tag%s\n"""%classname)
					py_class_file.write("""\t\treturn end_tag%s%s(%s)\n"""%(classname, "\x25", end_format[:-1]))
				py_class_file.write("""\tself.get_end       = get_end\n\n""")

				for attribute in classattributes:
					if attribute in ["pattern"]:
						py_class_file.write('\tself.{:<12} = params.get("{}", b"*")\n'.format(attribute,attribute))
					elif attribute in ["id","name"]:
						py_class_file.write('\tself.{:<12} = params.get("{}", b"%d"%id(self))\n'.format(attribute,attribute))
					elif attribute in ["disabled","active"]:
						py_class_file.write('\tself.{:<12} = params.get("{}", False)\n'.format(attribute,attribute))
					elif attribute in ["checked"]:
						py_class_file.write('\tself.{:<12} = params.get("{}", True)\n'.format(attribute,attribute))
					else:
						py_class_file.write('\tself.{:<12} = params.get("{}", b"")\n'.format(attribute,attribute))
				py_class_file.write('\treturn self\n')
			else:
				raise SyntaxError()
		else:
			if line.strip() != "":
				if len(stack) >= 1:
					stack[-1][1] += line.strip()
					stack[-1][2] += "# " +line.lstrip()

	py_class_file.close()
