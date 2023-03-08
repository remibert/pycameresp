""" Standard console redirector """

class Console:
	""" Console redirection """
	stdout = [None]

	@staticmethod
	def print(message, end=None):
		""" Redirected print """
		# pylint:disable=global-variable-not-assigned
		if Console.stdout[0] is None:
			if end is None:
				print(message)
			else:
				print(message, end=end)
		else:
			Console.stdout[0].write(message)
			if end is None:
				Console.stdout[0].write("\n")
			else:
				Console.stdout[0].write(end)

	@staticmethod
	def is_redirected():
		""" Indicates if the print is redirected """
		if Console.stdout[0] is None:
			return False
		return True

	@staticmethod
	def open(filename, attrib="w", encoding="utf8"):
		""" Open redirection """
		if Console.is_redirected():
			Console.close()
		Console.stdout[0] = open(filename, attrib, encoding=encoding)

	@staticmethod
	def close():
		""" Close redirection """
		if Console.is_redirected():
			Console.stdout[0].close()
			Console.stdout[0] = None
