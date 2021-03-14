# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from homekit import *

class OccupancySensor(Accessory):
	""" Occupancy homekit accessory """
	def __init__(self, **kwargs):
		""" Create occupancy accessory. Parameters : name(string), occupancyDetected(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SENSOR, **kwargs)

		self.server = Server(name=kwargs.get("name","Occupancy sensor"), serverUuid=Server.UUID_OCCUPANCY_SENSOR)
		self.occupancyDetected = charactUint8Create (Charact.UUID_OCCUPANCY_DETECTED, Charact.PERM_RE, kwargs.get("occupancyDetected",0))
		self.occupancyDetected.setConstraint(0, 1, 1)
		self.server.addCharact(self.occupancyDetected)

		self.addServer(self.server)
	
	def setOccupancyDetected(self, value):
		""" Set the occupancy detected """
		self.occupancyDetected.setValue(value)

def main():
	# Initialize homekit engine
	Homekit.init()

	# Create occupancy sensor
	sensor = OccupancySensor(name="My occupancy sensor", occupancyDetected=0)
	
	# Create accessory
	Homekit.play(sensor)

	import time
	occupancy = 0

	# Manage the occupancy (simple sample)
	while True:
		time.sleep(2)
		
		if occupancy == 0:
			occupancy = 1
		else:
			occupancy = 0

		# Change the accessory occupancy 
		sensor.setOccupancyDetected(occupancy)

if __name__ == "__main__":
	main()