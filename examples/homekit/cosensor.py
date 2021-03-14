# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from homekit import *

class CarbonMonoxideSensor(Accessory):
	""" Carbon monoxide homekit accessory """
	def __init__(self, **kwargs):
		""" Create carbon monoxide accessory. Parameters : name(string), carbonMonoxide(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SENSOR, **kwargs)

		self.server = Server(name=kwargs.get("name","Carbon monoxide sensor"), serverUuid=Server.UUID_CARBON_MONOXIDE_SENSOR)

		self.carbonMonoxideDetected = charactUint8Create (Charact.UUID_CARBON_MONOXIDE_DETECTED, Charact.PERM_RE, kwargs.get("carbonMonoxide",0))
		self.carbonMonoxideDetected.setConstraint(0, 1, 1)
		self.server.addCharact(self.carbonMonoxideDetected)

		self.addServer(self.server)
	
	def setCarbonMonoxide(self, value):
		""" Set the carbon monoxide """
		self.carbonMonoxideDetected.setValue(value)

def main():
	# Initialize homekit engine
	Homekit.init()

	# Create carbon monoxide sensor
	sensor = CarbonMonoxideSensor(name="My carbon monoxide sensor", carbonMonoxide=0)
	
	# Create accessory
	Homekit.play(sensor)

	import time
	carbonMonoxide = 0

	# Manage the carbon monoxide (simple sample)
	while True:
		time.sleep(2)
		
		if carbonMonoxide == 0:
			carbonMonoxide = 1
		else:
			carbonMonoxide = 0

		# Change the accessory carbon monoxide 
		sensor.setCarbonMonoxide(carbonMonoxide)

if __name__ == "__main__":
	main()