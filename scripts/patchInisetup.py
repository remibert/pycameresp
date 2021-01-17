
pyFilesToAdd = [
	"modules/main.py",
	"modules/welcome.py",
	"modules/sample.py"
]

if __name__ == "__main__":
	from sys import argv
	if len(argv) > 1:
		root = argv[1]
	else:
		root = "firmware"

	pyFileSetup='''
    with open("%s", "w") as f:
        f.write("""%s""")
'''
	from os.path import split
	patchIni=""
	for filename in pyFilesToAdd:
		patchPy = open(filename,"r").read()
		patchPy = patchPy.replace('"""',"'''")
		patchIni += pyFileSetup%(split(filename)[1],patchPy)

	inisetup = open("patch/python/micropython/ports/esp32/modules/inisetup.py","r").read()
	open(root + "/micropython/ports/esp32/modules/inisetup.py","w").write(inisetup%patchIni)
