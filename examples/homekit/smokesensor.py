# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Smoke homekit accessory """
from homekit import *

class SmokeSensor(Accessory):
	""" Smoke homekit accessory """
	def __init__(self, **kwargs):
		""" Create smoke accessory. Parameters : name(string), smoke_detected(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SENSOR, **kwargs)

		self.server = Server(name=kwargs.get("name","Smoke sensor"), server_uuid=Server.UUID_SMOKE_SENSOR)
		self.smoke_detected = charact_uint8_create (Charact.UUID_SMOKE_DETECTED, Charact.PERM_RE, kwargs.get("smoke_detected",0))
		self.smoke_detected.set_constraint(0, 1, 1)
		self.server.add_charact(self.smoke_detected)

		self.add_server(self.server)

	def set_smoke_detected(self, value):
		""" Set the smoke detected """
		self.smoke_detected.set_value(value)

def main():
	""" Test """
	# Initialize homekit engine
	Homekit.init()

	# Create smoke sensor
	sensor = SmokeSensor(name="My smoke sensor", smoke_detected=0)

	# Create accessory
	Homekit.play(sensor)

	import time
	smoke = 0

	# Manage the smoke (simple sample)
	while True:
		time.sleep(2)

		if smoke == 0:
			smoke = 1
		else:
			smoke = 0

		# Change the accessory smoke
		sensor.set_smoke_detected(smoke)

if __name__ == "__main__":
	main()
