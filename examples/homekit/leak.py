# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from homekit import *

class LeakSensor(Accessory):
	""" Leak homekit accessory """
	def __init__(self, **kwargs):
		""" Create leak accessory. Parameters : name(string), leakDetected(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SENSOR, **kwargs)

		self.server = Server(name=kwargs.get("name","Leak sensor"), serverUuid=Server.UUID_LEAK_SENSOR)
		self.leakDetected = charactUint8Create (Charact.UUID_LEAK_DETECTED, Charact.PERM_RE, kwargs.get("leakDetected",0))
		self.leakDetected.setConstraint(0, 1, 1)
		self.server.addCharact(self.leakDetected)

		self.addServer(self.server)
	
	def setLeakDetected(self, value):
		""" Set the leak detected """
		self.leakDetected.setValue(value)

def main():
	# Initialize homekit engine
	Homekit.init()

	# Create leak sensor
	sensor = LeakSensor(name="My leak sensor", leakDetected=0)
	
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
		sensor.setLeakDetected(leak)

if __name__ == "__main__":
	main()