# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Occupancy homekit accessory """
from homekit import *

class OccupancySensor(Accessory):
	""" Occupancy homekit accessory """
	def __init__(self, **kwargs):
		""" Create occupancy accessory. Parameters : name(string), occupancy_detected(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SENSOR, **kwargs)

		self.server = Server(name=kwargs.get("name","Occupancy sensor"), server_uuid=Server.UUID_OCCUPANCY_SENSOR)
		self.occupancy_detected = charact_uint8_create (Charact.UUID_OCCUPANCY_DETECTED, Charact.PERM_RE, kwargs.get("occupancy_detected",0))
		self.occupancy_detected.set_constraint(0, 1, 1)
		self.server.add_charact(self.occupancy_detected)

		self.add_server(self.server)

	def set_occupancy_detected(self, value):
		""" Set the occupancy detected """
		self.occupancy_detected.set_value(value)

def main():
	""" Test """
	# Initialize homekit engine
	Homekit.init()

	# Create occupancy sensor
	sensor = OccupancySensor(name="My occupancy sensor", occupancy_detected=0)

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
		sensor.set_occupancy_detected(occupancy)

if __name__ == "__main__":
	main()
