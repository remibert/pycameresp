import useful
import re
files = useful.scanFiles("../modules","*.py",["../modules/simul/*","*/__init__.py","*/welcome.py"])

regs = [
	'.*title\s*=\s*b(.*)',
	'.*text\s*=\s*b(.*)',
	'.*placeholder\s*=\s*b(.*)',
	'.*alert\s*=\s*b(.*)',
	'.*mainFrame\(request\s*,\s*response\s*,\s*args\s*,\s*b(.*)',
	'.*await\s*Notifier.notify\(\s*b(.*)',
]
from os.path import split, splitext
names = {}
for file in files:
	lines = open(file,"r").readlines()
	#~ print(file)
	name = splitext(split(file)[1])[0]
	ident = 0
	newlines = []
	for line in lines:
		found = False
		for reg in regs:
			spl = re.split(reg, line)
			if len(spl) > 1:
				text = ""
				terminator=spl[1][0]
				for char in spl[1][1:]:
					if char != terminator:
						text += char
					else:
						break
				
				msg = 'b%s%s%s'%(terminator,text,terminator)
				
				s = text.lower().split(" ")
				if len(s) == 1:
					field = s[0]
				elif len(s) == 2:
					field = s[0] + "_" + s[1]
				else:
					field = s[0] + "_" + s[1] + "_" + s[2]
					
				field_ = ""
				for char in field:
					if ord(char) >= ord("a") and ord(char) <= ord("z") or char == "_":
						field_ += char
				field = field_
				
				fieldname = "%s"%(field)
				if fieldname == "import":
					fieldname = "import_"
				printmess = True
				if fieldname not in names:
					names[fieldname] = msg
				else:
					if names[fieldname] != msg:
						ident += 1
						fieldname += "_%d"%ident
						names[fieldname] = msg
					else:
						printmess = False
					
				if printmess:
					print("%-40s=%s"%(fieldname, msg))
				line = line.replace(msg,"lang."+fieldname)
				found = True
		newlines.append(line)
	open(file, "w").writelines(newlines)
		#~ if found:
			#~ print(line)
