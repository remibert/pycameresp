# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Humidity homekit accessory """
from homekit import *

class HumiditySensor(Accessory):
	""" Humidity homekit accessory """
	def __init__(self, **kwargs):
		""" Create humidity sensor accessory. Parameters : name(string), humidity_level(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SENSOR, **kwargs)

		self.server = Server(name=kwargs.get("name","Humidity sensor"), server_uuid=Server.UUID_HUMIDITY_SENSOR)

		self.humidity_level = charact_float_create (Charact.UUID_CURRENT_RELATIVE_HUMIDITY, Charact.PERM_RE, kwargs.get("humidity_level",0.))
		self.humidity_level.set_constraint(0.0, 100.0, 1.0)
		self.humidity_level.set_unit(Charact.UNIT_PERCENTAGE)
		self.server.add_charact(self.humidity_level)

		self.add_server(self.server)

	def set_humidity_level(self, value):
		""" Set the humidity level """
		self.humidity_level.set_value(value)

def main():
	""" Test """
	# Initialize homekit engine
	Homekit.init()

	# Create humidity level sensor
	sensor = HumiditySensor(name="My humidity sensor", humidity_level=0.)

	# Create accessory
	Homekit.play(sensor)

	import time
	humidity_level = 0.

	# Manage the humidity level (simple sample)
	while True:
		time.sleep(2)

		humidity_level += 1.
		if humidity_level > 100.0:
			humidity_level = 0.0

		# Change the accessory humidity level
		sensor.set_humidity_level(humidity_level)

if __name__ == "__main__":
	main()
