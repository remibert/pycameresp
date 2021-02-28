# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from homekit import *

class LockMecanism(Accessory):
	""" Lock mecanism homekit accessory """
	def __init__(self, **kwargs):
		""" Create lock mecanism accessory. Parameters : name(string), lockCurrState(int), lockTargState(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_LOCK, **kwargs)
		self.server = Server(name=kwargs.get("name","Lock mecanism"), serverUuid=Server.UUID_LOCK_MECHANISM)

		self.lockCurrState = charactUint8Create (Charact.UUID_LOCK_CURRENT_STATE, Charact.PERM_RE, kwargs.get("lockCurrState",0))
		self.lockCurrState.setConstraint(0, 3, 1);
		self.server.addCharact(self.lockCurrState)

		self.lockTargState = charactUint8Create (Charact.UUID_LOCK_TARGET_STATE, Charact.PERM_RWE, kwargs.get("lockTargState",0))
		self.lockTargState.setConstraint(0, 1, 1)
		self.server.addCharact(self.lockTargState)

		self.lockTargState.setWriteCallback(self.writeLockTargState)
		self.addServer(self.server)

	def writeLockTargState(self, value):
		import time

		# Write target lock state
		self.lockTargState.setValue(value)

		if value == 1:
			print("Close lock")
		else:
			print("Open lock")

		time.sleep(3)
		# Set the current lock state
		self.lockCurrState.setValue(value)

		if value == 1:
			print("lock closed")
		else:
			print("lock opened")

def main():
	# Initialize homekit engine
	Homekit.init()
	
	# Create accessory
	Homekit.play(LockMecanism(name="My lock mecanism"))

if __name__ == "__main__":
	main()
