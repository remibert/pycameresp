# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Lightbulb homekit accessory """
from homekit import *

class Lightbulb(Accessory):
	""" Lightbulb homekit accessory """
	def __init__(self, **kwargs):
		""" Create lightbulb accessory. Parameters : name(string), on(bool), brigthness(int), saturation(float), hue(float) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_LIGHTING, **kwargs)
		self.server = Server(name=kwargs.get("name","Lightbulb"), server_uuid=Server.UUID_LIGHTBULB)

		self.on = charact_bool_create (Charact.UUID_ON, Charact.PERM_RWE, kwargs.get("on",True))
		self.on.set_write_callback(self.write_on)
		self.server.add_charact(self.on)

		self.brightness = charact_int_create (Charact.UUID_BRIGHTNESS, Charact.PERM_RWE, kwargs.get("brigthness",50))
		self.brightness.set_constraint(0, 100, 1)
		self.brightness.set_unit(Charact.UNIT_PERCENTAGE)
		self.brightness.set_write_callback(self.write_brightness)
		self.server.add_charact(self.brightness)

		self.saturation = charact_float_create (Charact.UUID_SATURATION, Charact.PERM_RWE, kwargs.get("saturation",50.))
		self.saturation.set_constraint(0.0, 100.0, 1.0)
		self.saturation.set_unit(Charact.UNIT_PERCENTAGE)
		self.saturation.set_write_callback(self.write_saturation)
		self.server.add_charact(self.saturation)

		self.hue = charact_float_create (Charact.UUID_HUE, Charact.PERM_RWE, kwargs.get("hue",50.))
		self.hue.set_constraint(0.0, 360.0, 1.0)
		self.hue.set_unit(Charact.UNIT_ARCDEGREES)
		self.hue.set_write_callback(self.write_hue)
		self.server.add_charact(self.hue)

		self.add_server(self.server)

	def write_on(self, value):
		""" Write on """
		if value:
			print("ON")
		else:
			print("OFF")
		self.on.set_value(value)

	def write_brightness(self, value):
		""" Write brightness """
		print("Brightness %f"%value)
		self.brightness.set_value(value)

	def write_saturation(self, value):
		""" Write saturation """
		print("Saturation %d"%value)
		self.saturation.set_value(value)

	def write_hue(self, value):
		""" Write hue """
		print("Hue %f"%value)
		self.hue.set_value(value)

def main():
	""" Test """
	# Initialize homekit engine
	Homekit.init()

	# Create accessory
	Homekit.play(Lightbulb(name="My lightbulb"))

if __name__ == "__main__":
	main()
