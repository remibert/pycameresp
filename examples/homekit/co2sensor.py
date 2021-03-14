# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from homekit import *

class CarbonDioxideSensor(Accessory):
	""" Carbon dioxide homekit accessory """
	def __init__(self, **kwargs):
		""" Create carbon dioxide accessory. Parameters : name(string), carbonDioxide(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SENSOR, **kwargs)

		self.server = Server(name=kwargs.get("name","Carbon dioxide sensor"), serverUuid=Server.UUID_CARBON_DIOXIDE_SENSOR)

		self.carbonDioxideDetected = charactUint8Create (Charact.UUID_CARBON_DIOXIDE_DETECTED, Charact.PERM_RE, kwargs.get("carbonDioxide",0))
		self.carbonDioxideDetected.setConstraint(0, 1, 1)
		self.server.addCharact(self.carbonDioxideDetected)

		self.addServer(self.server)
	
	def setCarbonDioxide(self, value):
		""" Set the carbon dioxide """
		self.carbonDioxideDetected.setValue(value)

def main():
	# Initialize homekit engine
	Homekit.init()

	# Create carbon dioxide sensor
	sensor = CarbonDioxideSensor(name="My carbon dioxide sensor", carbonDioxide=0)
	
	# Create accessory
	Homekit.play(sensor)

	import time
	carbonDioxide = 0

	# Manage the carbon dioxide (simple sample)
	while True:
		time.sleep(2)
		
		if carbonDioxide == 0:
			carbonDioxide = 1
		else:
			carbonDioxide = 0

		# Change the accessory carbon dioxide 
		sensor.setCarbonDioxide(carbonDioxide)

if __name__ == "__main__":
	main()