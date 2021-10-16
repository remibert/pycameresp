# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Leak homekit accessory """
from homekit import *

class LeakSensor(Accessory):
	""" Leak homekit accessory """
	def __init__(self, **kwargs):
		""" Create leak accessory. Parameters : name(string), leak_detected(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SENSOR, **kwargs)

		self.server = Server(name=kwargs.get("name","Leak sensor"), server_uuid=Server.UUID_LEAK_SENSOR)
		self.leak_detected = charact_uint8_create (Charact.UUID_LEAK_DETECTED, Charact.PERM_RE, kwargs.get("leak_detected",0))
		self.leak_detected.set_constraint(0, 1, 1)
		self.server.add_charact(self.leak_detected)

		self.add_server(self.server)

	def set_leak_detected(self, value):
		""" Set the leak detected """
		self.leak_detected.set_value(value)

def main():
	""" Test """
	# Initialize homekit engine
	Homekit.init()

	# Create leak sensor
	sensor = LeakSensor(name="My leak sensor", leak_detected=0)

	# Create accessory
	Homekit.play(sensor)

	import time
	leak = 0

	# Manage the leak (simple sample)
	while True:
		time.sleep(2)

		if leak == 0:
			leak = 1
		else:
			leak = 0

		# Change the accessory leak
		sensor.set_leak_detected(leak)

if __name__ == "__main__":
	main()
