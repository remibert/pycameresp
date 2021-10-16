# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Lock mecanism homekit accessory """
from homekit import *

class LockMecanism(Accessory):
	""" Lock mecanism homekit accessory """
	def __init__(self, **kwargs):
		""" Create lock mecanism accessory. Parameters : name(string), lock_curr_state(int), lock_targ_state(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_LOCK, **kwargs)
		self.server = Server(name=kwargs.get("name","Lock mecanism"), server_uuid=Server.UUID_LOCK_MECHANISM)

		self.lock_curr_state = charact_uint8_create (Charact.UUID_LOCK_CURRENT_STATE, Charact.PERM_RE, kwargs.get("lock_curr_state",0))
		self.lock_curr_state.set_constraint(0, 3, 1)
		self.server.add_charact(self.lock_curr_state)

		self.lock_targ_state = charact_uint8_create (Charact.UUID_LOCK_TARGET_STATE, Charact.PERM_RWE, kwargs.get("lock_targ_state",0))
		self.lock_targ_state.set_constraint(0, 1, 1)
		self.server.add_charact(self.lock_targ_state)

		self.lock_targ_state.set_write_callback(self.write_lock_targ_state)
		self.add_server(self.server)

	def write_lock_targ_state(self, value):
		""" Write lock target """
		import time

		# Write target lock state
		self.lock_targ_state.set_value(value)

		if value == 1:
			print("Close lock")
		else:
			print("Open lock")

		time.sleep(3)
		# Set the current lock state
		self.lock_curr_state.set_value(value)

		if value == 1:
			print("lock closed")
		else:
			print("lock opened")

def main():
	""" Test """
	# Initialize homekit engine
	Homekit.init()

	# Create accessory
	Homekit.play(LockMecanism(name="My lock mecanism"))

if __name__ == "__main__":
	main()
