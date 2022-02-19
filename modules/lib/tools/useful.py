# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Miscellaneous utility functions """
import sys
from tools import filesystem, logger

def run(filename):
	""" Import and execute python file """
	path, file = filesystem.split(filename)
	moduleName, _ = filesystem.splitext(file)

	if path not in sys.path:
		sys.path.append(path)

	try:
		del sys.modules[moduleName]
	except:
		pass
	try:
		exec("import %s"%moduleName)

		for fct in dir(sys.modules[moduleName]):
			if fct == "main":
				print("Start main function")
				sys.modules[moduleName].main()
				break
	except Exception as err:
		logger.syslog(err)
	except KeyboardInterrupt as err:
		logger.syslog(err)
