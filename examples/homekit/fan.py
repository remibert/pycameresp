# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from homekit import *

class Fan(Accessory):
	""" Fan homekit accessory """
	def __init__(self, **kwargs):
		""" Create fan accessory. Parameters : name(string), on(bool), direction(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_FAN, **kwargs)
		self.server = Server(name=kwargs.get("name","Fan"), serverUuid=Server.UUID_FAN)
		
		self.on = charactBoolCreate (Charact.UUID_ON, Charact.PERM_RWE, kwargs.get("on",True))
		self.on.setWriteCallback(self.writeOn)
		self.server.addCharact(self.on)
		
		self.direction = charactIntCreate (Charact.UUID_ROTATION_DIRECTION, Charact.PERM_RWE, kwargs.get("direction",0))
		self.direction.setConstraint(0, 1, 1)
		self.direction.setWriteCallback(self.writeDirection)
		self.server.addCharact(self.direction)
		
		self.addServer(self.server)

	def writeOn(self, value):
		if value:
			print("ON")
		else:
			print("OFF")
		self.on.setValue(value)

	def writeDirection(self, value):
		if value:
			print("RIGHT")
		else:
			print("LEFT")
		self.direction.setValue(value)

def main():
	# Initialize homekit engine
	Homekit.init()
	
	# Create accessory
	Homekit.play(Fan(name="My fan"))

if __name__ == "__main__":
	main()