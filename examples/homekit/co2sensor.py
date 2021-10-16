# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Carbon dioxide homekit accessory """
from homekit import *

class CarbonDioxideSensor(Accessory):
	""" Carbon dioxide homekit accessory """
	def __init__(self, **kwargs):
		""" Create carbon dioxide accessory. Parameters : name(string), carbon_dioxide(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SENSOR, **kwargs)

		self.server = Server(name=kwargs.get("name","Carbon dioxide sensor"), server_uuid=Server.UUID_CARBON_DIOXIDE_SENSOR)

		self.carbon_dioxide_detected = charact_uint8_create (Charact.UUID_CARBON_DIOXIDE_DETECTED, Charact.PERM_RE, kwargs.get("carbon_dioxide",0))
		self.carbon_dioxide_detected.set_constraint(0, 1, 1)
		self.server.add_charact(self.carbon_dioxide_detected)

		self.add_server(self.server)

	def set_carbon_dioxide(self, value):
		""" Set the carbon dioxide """
		self.carbon_dioxide_detected.set_value(value)

def main():
	""" Test """
	# Initialize homekit engine
	Homekit.init()

	# Create carbon dioxide sensor
	sensor = CarbonDioxideSensor(name="My carbon dioxide sensor", carbon_dioxide=0)

	# Create accessory
	Homekit.play(sensor)

	import time
	carbon_dioxide = 0

	# Manage the carbon dioxide (simple sample)
	while True:
		time.sleep(2)

		if carbon_dioxide == 0:
			carbon_dioxide = 1
		else:
			carbon_dioxide = 0

		# Change the accessory carbon dioxide
		sensor.set_carbon_dioxide(carbon_dioxide)

if __name__ == "__main__":
	main()
 