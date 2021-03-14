# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from homekit import *

class SmokeSensor(Accessory):
	""" Smoke homekit accessory """
	def __init__(self, **kwargs):
		""" Create smoke accessory. Parameters : name(string), smokeDetected(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SENSOR, **kwargs)

		self.server = Server(name=kwargs.get("name","Smoke sensor"), serverUuid=Server.UUID_SMOKE_SENSOR)
		self.smokeDetected = charactUint8Create (Charact.UUID_SMOKE_DETECTED, Charact.PERM_RE, kwargs.get("smokeDetected",0))
		self.smokeDetected.setConstraint(0, 1, 1)
		self.server.addCharact(self.smokeDetected)

		self.addServer(self.server)
	
	def setSmokeDetected(self, value):
		""" Set the smoke detected """
		self.smokeDetected.setValue(value)

def main():
	# Initialize homekit engine
	Homekit.init()

	# Create smoke sensor
	sensor = SmokeSensor(name="My smoke sensor", smokeDetected=0)
	
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
		sensor.setSmokeDetected(smoke)

if __name__ == "__main__":
	main()