# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from homekit import *

class HumiditySensor(Accessory):
	""" Humidity homekit accessory """
	def __init__(self, **kwargs):
		""" Create humidity sensor accessory. Parameters : name(string), humidityLevel(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SENSOR, **kwargs)

		self.server = Server(name=kwargs.get("name","Humidity sensor"), serverUuid=Server.UUID_HUMIDITY_SENSOR)

		self.humidityLevel = charactFloatCreate (Charact.UUID_CURRENT_RELATIVE_HUMIDITY, Charact.PERM_RE, kwargs.get("humidityLevel",0.))
		self.humidityLevel.setConstraint(0.0, 100.0, 1.0)
		self.humidityLevel.setUnit(Charact.UNIT_PERCENTAGE)
		self.server.addCharact(self.humidityLevel)

		self.addServer(self.server)
	
	def setHumidityLevel(self, value):
		""" Set the humidity level """
		self.humidityLevel.setValue(value)

def main():
	# Initialize homekit engine
	Homekit.init()

	# Create humidity level sensor
	sensor = HumiditySensor(name="My humidity sensor", humidityLevel=0.)
	
	# Create accessory
	Homekit.play(sensor)

	import time
	humidityLevel = 0.

	# Manage the humidity level (simple sample)
	while True:
		time.sleep(2)

		humidityLevel += 1.
		if humidityLevel > 100.0:
			humidityLevel = 0.0

		# Change the accessory humidity level 
		sensor.setHumidityLevel(humidityLevel)

if __name__ == "__main__":
	main()