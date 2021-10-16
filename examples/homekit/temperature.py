# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Temperature homekit accessory """
from homekit import *

class TemperatureSensor(Accessory):
	""" Temperature homekit accessory """
	def __init__(self, **kwargs):
		""" Create temperature accessory. Parameters : name(string), temperature(float) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SENSOR, **kwargs)

		self.server = Server(name=kwargs.get("name","Temperature"), server_uuid=Server.UUID_TEMPERATURE_SENSOR)

		self.temperature = charact_float_create (Charact.UUID_CURRENT_TEMPERATURE, Charact.PERM_RE, kwargs.get("temperature",20.))
		self.temperature.set_constraint(0.0, 100.0, 0.1)
		self.temperature.set_unit(Charact.UNIT_CELSIUS)
		self.server.add_charact(self.temperature)

		self.add_server(self.server)

	def set_temperature(self, temp):
		""" Set the temperature """
		self.temperature.set_value(temp)

def main():
	""" Test """
	# Initialize homekit engine
	Homekit.init()

	# Create temperature sensor
	sensor = TemperatureSensor(name="My temperature sensor", temperature=10.)

	# Create accessory
	Homekit.play(sensor)

	import time
	temperature = 0.0

	# Manage the temperature (simple sample)
	while True:
		time.sleep(2)

		temperature += 1.
		if temperature > 100.0:
			temperature = 0.0

		# Change the accessory temperature
		sensor.set_temperature(temperature)

if __name__ == "__main__":
	main()
