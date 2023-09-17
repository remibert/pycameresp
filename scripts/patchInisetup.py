""" Patch the initsetup.py """
# pylint:disable=consider-using-f-string
# pylint:disable=unspecified-encoding
from zlib import *
from binascii import *

files_to_add = [
	("","modules/main.py"),
	("","modules/pycameresp.py"),
]

if __name__ == "__main__":
	from sys import argv
	if len(argv) > 1:
		root = argv[1]
		micro = argv[2]
	else:
		root = "firmware"

	file_setup_begin='''
    print("Install %(filename)s")
    with open("%(filename)s", "w") as f:
%(content)s
'''
	file_setup_next='''        f.write(decompress(a2b_base64(%s)))
'''
	from os.path import split
	patch_ini=""
	import glob
	for filename in glob.glob("modules/www/*.css"):
		files_to_add.append(("www",filename))
	for filename in glob.glob("modules/www/*.js"):
		files_to_add.append(("www",filename))
	for path, filename in files_to_add:
		content = ""
		file = open(filename, "rb")
		while True:
			part = file.read(8192)
			if part == b"":
				break
			content += file_setup_next % b2a_base64(compress(part))
		if path != "":
			patch_ini += "    try:\n        uos.mkdir('%s')\n    except: pass\n"%path
			filename = "%s/%s"%(path, split(filename)[1])
		else:
			filename = split(filename)[1]
		patch_ini += file_setup_begin%locals()
	
	patch_ini += "    import machine\n"
	patch_ini += "    print('Forced reboot after installation')\n"
	patch_ini += "    machine.deepsleep(1000)\n"

	inisetup = open("patch/%s/python/micropython/ports/esp32/modules/inisetup.py"%micro,"r").read()
	open(root + "/ports/esp32/modules/inisetup.py","w").write(inisetup%patch_ini)
	inisetup = open("patch/%s/python/micropython/ports/rp2/modules/_boot.py"%micro,"r").read()
	open(root + "/ports/rp2/modules/_boot.py","w").write(inisetup%patch_ini)
	import time
	year,month,day,hour,minute,second,weekday,yearday = time.localtime()[:8]
	open("modules/lib/tools/builddate.py","w").write("''' Build date '''\ndate=b'%04d/%02d/%02d  %02d:%02d:%02d'\n"%(year,month,day,hour,minute,second))
