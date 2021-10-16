# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Light homekit accessory """
from homekit import *

class LightSensor(Accessory):
	""" Light homekit accessory """
	def __init__(self, **kwargs):
		""" Create light sensor accessory. Parameters : name(string), light_level(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SENSOR, **kwargs)

		self.server = Server(name=kwargs.get("name","Light sensor"), server_uuid=Server.UUID_LIGHT_SENSOR)

		self.light_level = charact_float_create (Charact.UUID_CURRENT_AMBIENT_LIGHT_LEVEL, Charact.PERM_RE, kwargs.get("light_level",0.))
		self.light_level.set_constraint(0.0001, 100000.0, 0.0)
		self.light_level.set_unit(Charact.UNIT_LUX)
		self.server.add_charact(self.light_level)

		self.add_server(self.server)

	def set_light_level(self, value):
		""" Set the light level """
		self.light_level.set_value(value)

def main():
	""" Test """
	# Initialize homekit engine
	Homekit.init()

	# Create light level sensor
	sensor = LightSensor(name="My light sensor", light_level=0.)

	# Create accessory
	Homekit.play(sensor)

	import time
	light_level = 0.

	# Manage the light level (simple sample)
	while True:
		time.sleep(2)

		light_level += 1.
		if light_level > 100.0:
			light_level = 0.0

		# Change the accessory light level
		sensor.set_light_level(light_level)

if __name__ == "__main__":
	main()
