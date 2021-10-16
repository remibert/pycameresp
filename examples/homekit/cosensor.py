# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Carbon monoxide homekit accessory """
from homekit import *

class CarbonMonoxideSensor(Accessory):
	""" Carbon monoxide homekit accessory """
	def __init__(self, **kwargs):
		""" Create carbon monoxide accessory. Parameters : name(string), carbon_monoxide(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SENSOR, **kwargs)

		self.server = Server(name=kwargs.get("name","Carbon monoxide sensor"), server_uuid=Server.UUID_CARBON_MONOXIDE_SENSOR)

		self.carbon_monoxide_detected = charact_uint8_create (Charact.UUID_CARBON_MONOXIDE_DETECTED, Charact.PERM_RE, kwargs.get("carbon_monoxide",0))
		self.carbon_monoxide_detected.set_constraint(0, 1, 1)
		self.server.add_charact(self.carbon_monoxide_detected)

		self.add_server(self.server)

	def set_carbon_monoxide(self, value):
		""" Set the carbon monoxide """
		self.carbon_monoxide_detected.set_value(value)

def main():
	""" Test """
	# Initialize homekit engine
	Homekit.init()

	# Create carbon monoxide sensor
	sensor = CarbonMonoxideSensor(name="My carbon monoxide sensor", carbon_monoxide=0)

	# Create accessory
	Homekit.play(sensor)

	import time
	carbon_monoxide = 0

	# Manage the carbon monoxide (simple sample)
	while True:
		time.sleep(2)

		if carbon_monoxide == 0:
			carbon_monoxide = 1
		else:
			carbon_monoxide = 0

		# Change the accessory carbon monoxide
		sensor.set_carbon_monoxide(carbon_monoxide)

if __name__ == "__main__":
	main()
