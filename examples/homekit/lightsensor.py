# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from homekit import *

class LightSensor(Accessory):
	""" Light homekit accessory """
	def __init__(self, **kwargs):
		""" Create light sensor accessory. Parameters : name(string), lightLevel(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SENSOR, **kwargs)

		self.server = Server(name=kwargs.get("name","Light sensor"), serverUuid=Server.UUID_LIGHT_SENSOR)

		self.lightLevel = charactFloatCreate (Charact.UUID_CURRENT_AMBIENT_LIGHT_LEVEL, Charact.PERM_RE, kwargs.get("lightLevel",0.))
		self.lightLevel.setConstraint(0.0001, 100000.0, 0.0)
		self.lightLevel.setUnit(Charact.UNIT_LUX)
		self.server.addCharact(self.lightLevel)

		self.addServer(self.server)
	
	def setLightLevel(self, value):
		""" Set the light level """
		self.lightLevel.setValue(value)

def main():
	# Initialize homekit engine
	Homekit.init()

	# Create light level sensor
	sensor = LightSensor(name="My light sensor", lightLevel=0.)
	
	# Create accessory
	Homekit.play(sensor)

	import time
	lightLevel = 0.

	# Manage the light level (simple sample)
	while True:
		time.sleep(2)

		lightLevel += 1.
		if lightLevel > 100.0:
			lightLevel = 0.0

		# Change the accessory light level 
		sensor.setLightLevel(lightLevel)

if __name__ == "__main__":
	main()