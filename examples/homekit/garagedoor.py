# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Garage door opener homekit accessory """
from homekit import *

class GarageDoorOpener(Accessory):
	""" Garage door opener homekit accessory """
	def __init__(self, **kwargs):
		""" Create door opener accessory. Parameters : name(string), curr_door_state(int), targ_door_state(int), obstr_detect(bool) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_GARAGE_DOOR_OPENER, **kwargs)
		self.server = Server(name=kwargs.get("name","Garage door"), server_uuid=Server.UUID_GARAGE_DOOR_OPENER)

		self.curr_door_state = charact_uint8_create (Charact.UUID_CURRENT_DOOR_STATE, Charact.PERM_RE, kwargs.get("curr_door_state",0))
		self.curr_door_state .set_constraint(0, 4, 1)
		self.server.add_charact(self.curr_door_state)

		self.targ_door_state = charact_uint8_create (Charact.UUID_TARGET_DOOR_STATE, Charact.PERM_RWE, kwargs.get("targ_door_state",0))
		self.targ_door_state.set_constraint(0, 1, 1)
		self.server.add_charact(self.targ_door_state)

		self.obstr_detect = charact_bool_create (Charact.UUID_OBSTRUCTION_DETECTED, Charact.PERM_RE, kwargs.get("obstr_detect",False))
		self.server.add_charact(self.obstr_detect)

		self.targ_door_state.set_write_callback(self.write_targ_door_state)
		self.add_server(self.server)

	def write_targ_door_state(self, charact):
		""" Write target door state """
		import time

		# Close or open door
		if charact.get_value() == 1:
			print("Close door")
		else:
			print("Open door")

		time.sleep(3)

		# Set the current door state
		self.curr_door_state.set_value(charact.get_value())

		if charact.get_value() == 1:
			print("Door closed")
		else:
			print("Door opened")

def main():
	""" Test """
	# Initialize homekit engine
	Homekit.init()

	# Create accessory
	Homekit.play(GarageDoorOpener(name="My garage door"))

if __name__ == "__main__":
	main()
