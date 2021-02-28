# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from homekit import *

class Switch(Accessory):
	""" Switch homekit accessory """
	def __init__(self, **kwargs):
		""" Create switch accessory. Parameters : name(string), on(bool) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SWITCH, **kwargs)
		self.server = Server(name=kwargs.get("name","Switch"), serverUuid=Server.UUID_SWITCH)
		
		self.on = charactBoolCreate (Charact.UUID_ON, Charact.PERM_RWE, kwargs.get("on",True))
		self.server.addCharact(self.on)
		self.on.setWriteCallback(self.writeOn)
		self.addServer(self.server)

	def writeOn(self, value):
		if value:
			print("ON")
		else:
			print("OFF")
		self.on.setValue(value)

def main():
	# Initialize homekit engine
	Homekit.init()
	
	# Create accessory
	Homekit.play(Switch(name="My Switch"))

if __name__ == "__main__":
	main()