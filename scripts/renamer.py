from useful import scanAll
from re import split, match

def replacer(files, regexp, sourceC):
	replacement = {}
	for file in files:
		for line in open(file,"r").readlines():
			spl = split(regexp,line)
			if len(spl) > 1:
				if spl[1].lower() != spl[1]:
					name = spl[1]
					newName = ""
					previousLetter = ""
					for letter in name:
						if ord(letter) >= ord('A') and ord(letter) <= ord('Z'):
							if newName != "":
								if ord(previousLetter) >= ord('A') and ord(previousLetter) <= ord('Z') or previousLetter == "_":
									newName += letter.lower()
								else:
									newName += "_" + letter.lower()
							else:
								newName += letter.lower()
						else:
							newName += letter
						previousLetter = letter
					replacement[name] = newName
	replacement = list(replacement.items())
	replacement.sort()
	replacement.reverse()
	
	from os.path import splitext
	
	for file in files:
		newLines = []
		print(file)
		replaceAll = False
		if sourceC:
			if splitext(file) in [".c",".h"]:
				replaceAll = True
			
		for line in open(file,"r").readlines():
			for name, newName in replacement:
				#~ print(name,newName)
				pos = line.find(name)
				if pos != -1:
					previous = line[pos-1]
					after = line[pos + len(name)]
					if (previous.isalnum() or after.isalnum()) and replaceAll == False:
						#~ print("--->",name, previous, after)
						#~ print(line)
						pass
					else:
						line = line.replace(name, newName)
			newLines.append(line)
		open(file ,"w").writelines(newLines)

if __name__ == "__main__":
	all_, files, directories = scanAll("pycameresp", includes = ["*.py","*.h","*.c"], excludes = [])
	replacer(files, "\s*def\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\(.*\)\s*:.*", True)
	replacer(files, "\s*self\s*\.\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=.*", False)