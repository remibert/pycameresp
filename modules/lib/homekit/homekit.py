# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
class Homekit:
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
	def addAccessory(accessory):
		""" Add accessory to homekit data base """
		import homekit_
		homekit_.addAccessory(accessory.accessory)

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
	def setSetupId(setupId):
		""" Initialize setup id (length must be 4 bytes) """
		import homekit_
		homekit_.setSetupId(setupId)

	@staticmethod
	def setSetupCode(setupCode):
		""" Set the setup code (format must be 'xxx-xx-xxx') """
		import homekit_
		homekit_.setSetupCode(setupCode)
	
	@staticmethod
	def eraseAll():
		""" Stop homekit engine and remove the data of all homekit accessories """
		import homekit_
		homekit_.stop()
		homekit_.deinit()
		homekit_.eraseAll()

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
		Homekit.addAccessory(accessory)
		
		# Initialize setup id (length must be 4 bytes)
		Homekit.setSetupId(setupId)
		
		# Initialize setup code (format must be 'xxx-xx-xxx')
		Homekit.setSetupCode(setupCode)
		
		# Start homekit
		Homekit.start()