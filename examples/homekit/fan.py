# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Fan homekit accessory """
from homekit import *

class Fan(Accessory):
	""" Fan homekit accessory """
	def __init__(self, **kwargs):
		""" Create fan accessory. Parameters : name(string), on(bool), direction(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_FAN, **kwargs)
		self.server = Server(name=kwargs.get("name","Fan"), server_uuid=Server.UUID_FAN)

		self.on = charact_bool_create (Charact.UUID_ON, Charact.PERM_RWE, kwargs.get("on",True))
		self.on.set_write_callback(self.write_on)
		self.server.add_charact(self.on)

		self.direction = charact_int_create (Charact.UUID_ROTATION_DIRECTION, Charact.PERM_RWE, kwargs.get("direction",0))
		self.direction.set_constraint(0, 1, 1)
		self.direction.set_write_callback(self.write_direction)
		self.server.add_charact(self.direction)

		self.add_server(self.server)

	def write_on(self, value):
		""" Write on """
		if value:
			print("ON")
		else:
			print("OFF")
		self.on.set_value(value)

	def write_direction(self, value):
		""" Write direction """
		if value:
			print("RIGHT")
		else:
			print("LEFT")
		self.direction.set_value(value)

def main():
	""" Test """
	# Initialize homekit engine
	Homekit.init()

	# Create accessory
	Homekit.play(Fan(name="My fan"))

if __name__ == "__main__":
	main()
