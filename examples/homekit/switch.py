# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Switch homekit accessory """
from homekit import *

class Switch(Accessory):
	""" Switch homekit accessory """
	def __init__(self, **kwargs):
		""" Create switch accessory. Parameters : name(string), on(bool) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SWITCH, **kwargs)
		self.server = Server(name=kwargs.get("name","Switch"), server_uuid=Server.UUID_SWITCH)

		self.on = charact_bool_create (Charact.UUID_ON, Charact.PERM_RWE, kwargs.get("on",True))
		self.server.add_charact(self.on)
		self.on.set_write_callback(self.write_on)
		self.add_server(self.server)

	def write_on(self, charact):
		""" Write on """
		if charact.get_value():
			print("ON")
		else:
			print("OFF")

def main():
	""" Test """
	# Initialize homekit engine
	Homekit.init()

	# Create accessory
	Homekit.play(Switch(name="My Switch"))

if __name__ == "__main__":
	main()
