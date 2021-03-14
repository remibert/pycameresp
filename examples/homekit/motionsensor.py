# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from homekit import *

class MotionSensor(Accessory):
	""" Motion homekit accessory """
	def __init__(self, **kwargs):
		""" Create motion accessory. Parameters : name(string), motionDetected(bool) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SENSOR, **kwargs)

		self.server = Server(name=kwargs.get("name","Motion sensor"), serverUuid=Server.UUID_MOTION_SENSOR)
		self.motionDetected = charactBoolCreate (Charact.UUID_MOTION_DETECTED, Charact.PERM_RE, kwargs.get("motionDetected",False))
		self.server.addCharact(self.motionDetected)

		self.addServer(self.server)
	
	def setMotionDetected(self, value):
		""" Set the motion detected """
		self.motionDetected.setValue(value)

def main():
	# Initialize homekit engine
	Homekit.init()

	# Create motion sensor
	sensor = MotionSensor(name="My motion sensor", motionDetected=False)
	
	# Create accessory
	Homekit.play(sensor)

	import time
	motion = False

	# Manage the motion (simple sample)
	while True:
		time.sleep(2)
		
		if motion == False:
			motion = True
		else:
			motion = False

		# Change the accessory motion 
		sensor.setMotionDetected(motion)

if __name__ == "__main__":
	main()