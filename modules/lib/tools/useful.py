# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Miscellaneous utility functions """
import sys
import io
import tools.logger
import tools.filesystem

def run(filename):
	""" Import and execute python file """
	result = None
	path, file = tools.filesystem.split(filename)
	module_name, _ = tools.filesystem.splitext(file)

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
		if tools.filesystem.ismicropython():
			out = io.StringIO()
			# pylint: disable=no-member
			sys.print_exception(err, out)
			try:
				line_err = out.getvalue().split("\n")[-3]
				result = int((line_err.split(',')[1]).split(" ")[-1])
			except:
				pass
		tools.logger.syslog(err)
	except KeyboardInterrupt as err:
		tools.logger.syslog(err)
	return result
