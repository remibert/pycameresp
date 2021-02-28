# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from homekit import *

class TemperatureSensor(Accessory):
	""" Temperature homekit accessory """
	def __init__(self, **kwargs):
		""" Create fan accessory. Parameters : name(string), temperature(float) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SENSOR, **kwargs)
		
		self.server = Server(name=kwargs.get("name","Temperature"), serverUuid=Server.UUID_TEMPERATURE_SENSOR)
		self.temperature = charactFloatCreate (Charact.UUID_CURRENT_TEMPERATURE, Charact.PERM_RE, kwargs.get("temperature",20.))
		self.temperature.setConstraint(0.0, 100.0, 0.1)
		self.temperature.setUnit(Charact.UNIT_CELSIUS)
		self.server.addCharact(self.temperature)

		self.addServer(self.server)
	
	def setTemperature(self, temp):
		""" Set the temperature """
		self.temperature.setValue(temp)

def main():
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
		
		temperature += 1.0
		if temperature > 100.0:
			temperature = 0.0

		# Change the accessory temperature 
		sensor.setTemperature(temperature)

if __name__ == "__main__":
	main()