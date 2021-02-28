# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from homekit import *

class Lightbulb(Accessory):
	""" Lightbulb homekit accessory """
	def __init__(self, **kwargs):
		""" Create lightbulb accessory. Parameters : name(string), on(bool), brigthness(int), saturation(float), hue(float) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_LIGHTING, **kwargs)
		self.server = Server(name=kwargs.get("name","Lightbulb"), serverUuid=Server.UUID_LIGHTBULB)
		
		self.on = charactBoolCreate (Charact.UUID_ON, Charact.PERM_RWE, kwargs.get("on",True))
		self.on.setWriteCallback(self.writeOn)
		self.server.addCharact(self.on)
		
		self.brightness = charactIntCreate (Charact.UUID_BRIGHTNESS, Charact.PERM_RWE, kwargs.get("brigthness",50))
		self.brightness.setConstraint(0, 100, 1)
		self.brightness.setUnit(Charact.UNIT_PERCENTAGE)
		self.brightness.setWriteCallback(self.writeBrightness)
		self.server.addCharact(self.brightness)
		
		self.saturation = charactFloatCreate (Charact.UUID_SATURATION, Charact.PERM_RWE, kwargs.get("saturation",50.))
		self.saturation.setConstraint(0.0, 100.0, 1.0)
		self.saturation.setUnit(Charact.UNIT_PERCENTAGE)
		self.saturation.setWriteCallback(self.writeSaturation)
		self.server.addCharact(self.saturation)
		
		self.hue = charactFloatCreate (Charact.UUID_HUE, Charact.PERM_RWE, kwargs.get("hue",50.))
		self.hue.setConstraint(0.0, 360.0, 1.0)
		self.hue.setUnit(Charact.UNIT_ARCDEGREES)
		self.hue.setWriteCallback(self.writeHue)
		self.server.addCharact(self.hue)
		
		self.addServer(self.server)
		
	def writeOn(self, value):
		if value:
			print("ON")
		else:
			print("OFF")
		self.on.setValue(value)

	def writeBrightness(self, value):
		print("Brightness %f"%value)
		self.brightness.setValue(value)

	def writeSaturation(self, value):
		print("Saturation %d"%value)
		self.saturation.setValue(value)

	def writeHue(self, value):
		print("Hue %f"%value)
		self.hue.setValue(value)

def main():
	# Initialize homekit engine
	Homekit.init()

	# Create accessory
	Homekit.play(Lightbulb(name="My lightbulb"))

if __name__ == "__main__":
	main()