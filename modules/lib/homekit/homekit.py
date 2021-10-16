""" Homekit main class """
# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
class Homekit:
	""" Homekit main class """
	@staticmethod
	def start():
		""" Start home kit engine """
		import homekit_
		homekit_.start()

	@staticmethod
	def stop():
		""" Stop homekit engine """
		import homekit_
		homekit_.stop()

	@staticmethod
	def add_accessory(accessory):
		""" Add accessory to homekit data base """
		import homekit_
		homekit_.add_accessory(accessory.accessory)

	@staticmethod
	def init():
		""" Initialize homekit """
		import homekit_
		homekit_.init()

	@staticmethod
	def deinit():
		""" Deinit homekit """
		import homekit_
		homekit_.deinit()

	@staticmethod
	def set_setup_id(setupId):
		""" Initialize setup id (length must be 4 bytes) """
		import homekit_
		homekit_.set_setup_id(setupId)

	@staticmethod
	def set_setup_code(setupCode):
		""" Set the setup code (format must be 'xxx-xx-xxx') """
		import homekit_
		homekit_.set_setup_code(setupCode)

	@staticmethod
	def erase_all():
		""" Stop homekit engine and remove the data of all homekit accessories """
		import homekit_
		homekit_.stop()
		homekit_.deinit()
		homekit_.erase_all()

	@staticmethod
	def reboot():
		""" Stop homekit, deinit, init and start """
		import homekit_
		homekit_.stop()
		homekit_.deinit()
		homekit_.init()
		homekit_.start()

	@staticmethod
	def play(accessory, setupCode="111-11-111", setupId="ESP3"):
		""" Register accessory, start homekit engine """
		# Add accessory to homekit
		Homekit.add_accessory(accessory)

		# Initialize setup id (length must be 4 bytes)
		Homekit.set_setup_id(setupId)

		# Initialize setup code (format must be 'xxx-xx-xxx')
		Homekit.set_setup_code(setupCode)

		# Start homekit
		Homekit.start()
