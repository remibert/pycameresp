# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from homekit import *

class GarageDoorOpener(Accessory):
	""" Garage door opener homekit accessory """
	def __init__(self, **kwargs):
		""" Create door opener accessory. Parameters : name(string), currDoorState(int), targDoorState(int), obstrDetect(bool) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_GARAGE_DOOR_OPENER, **kwargs)
		self.server = Server(name=kwargs.get("name","Garage door"), serverUuid=Server.UUID_GARAGE_DOOR_OPENER)
		
		self.currDoorState = charactUint8Create (Charact.UUID_CURRENT_DOOR_STATE, Charact.PERM_RE, kwargs.get("currDoorState",0))
		self.currDoorState .setConstraint(0, 4, 1)
		self.server.addCharact(self.currDoorState)
		
		self.targDoorState = charactUint8Create (Charact.UUID_TARGET_DOOR_STATE, Charact.PERM_RWE, kwargs.get("targDoorState",0))
		self.targDoorState.setConstraint(0, 1, 1)
		self.server.addCharact(self.targDoorState)
		
		self.obstrDetect = charactBoolCreate (Charact.UUID_OBSTRUCTION_DETECTED, Charact.PERM_RE, kwargs.get("obstrDetect",False))
		self.server.addCharact(self.obstrDetect)

		self.targDoorState.setWriteCallback(self.writeTargDoorState)
		self.addServer(self.server)

	def writeTargDoorState(self, value):
		import time

		# Write target door state
		self.targDoorState.setValue(value)

		if value == 1:
			print("Close door")
		else:
			print("Open door")

		time.sleep(3)
		# Set the current door state
		self.currDoorState.setValue(value)

		if value == 1:
			print("Door closed")
		else:
			print("Door opened")

def main():
	# Initialize homekit engine
	Homekit.init()
	
	# Create accessory
	Homekit.play(GarageDoorOpener(name="My garage door"))

if __name__ == "__main__":
	#~ main()
	for i in range(4,-1,-1):
		print(i)