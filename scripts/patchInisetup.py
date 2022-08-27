""" Patch the initsetup.py """
# pylint:disable=consider-using-f-string
# pylint:disable=unspecified-encoding

filesToAdd = [
	("","modules/main.py"),
	("","modules/pycameresp.py"),
	("","modules/sample.py"),
]

if __name__ == "__main__":
	from sys import argv
	if len(argv) > 1:
		root = argv[1]
	else:
		root = "firmware"

	fileSetup='''
    with open("%(filename)s", "w") as f:
        f.write("""%(content)s""")
'''
	from os.path import split
	patchIni=""
	import glob
	for filename in glob.glob("modules/www/*.css"):
		if not "bootstrap" in filename:
			filesToAdd.append(("www",filename))
	for path, filename in filesToAdd:
		content = open(filename,"r").read()
		content = content.replace('"""',"'''")
		content = content.replace("\x5C","\x5C\x5C") # Replace \ by \\
		if path != "":
			patchIni += "    try:\n        uos.mkdir('%s')\n    except: pass\n"%path
			filename = "%s/%s"%(path, split(filename)[1])
		else:
			filename = split(filename)[1]
		patchIni += fileSetup%locals()

	inisetup = open("patch/python/micropython/ports/esp32/modules/inisetup.py","r").read()
	open(root + "/micropython/ports/esp32/modules/inisetup.py","w").write(inisetup%patchIni)
	import time
	year,month,day,hour,minute,second,weekday,yearday = time.localtime()[:8]
	open("modules/lib/tools/builddate.py","w").write("''' Build date '''\ndate=b'%04d/%02d/%02d  %02d:%02d:%02d'\n"%(year,month,day,hour,minute,second))
