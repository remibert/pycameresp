# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Miscellaneous utility functions """
import sys
import io
try:
	from tools import logger,filesystem
except:
	# pylint:disable=multiple-imports
	import logger,filesystem

def run(filename):
	""" Import and execute python file """
	result = None
	path, file = filesystem.split(filename)
	module_name, _ = filesystem.splitext(file)

	if path not in sys.path:
		sys.path.append(path)

	try:
		del sys.modules[module_name]
	except:
		pass

	try:
		exec("import %s"%module_name)
		for fct in dir(sys.modules[module_name]):
			if fct == "main":
				print("Execute main function")
				sys.modules[module_name].main()
				break
	except Exception as err:
		if filesystem.ismicropython():
			out = io.StringIO()
			# pylint: disable=no-member
			sys.print_exception(err, out)
			try:
				line_err = out.getvalue().split("\n")[-3]
				result = int((line_err.split(',')[1]).split(" ")[-1])
			except:
				pass
		logger.syslog(err)
	except KeyboardInterrupt as err:
		logger.syslog(err)
	return result
