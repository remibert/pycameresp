# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Motion homekit accessory """
from homekit import *

class MotionSensor(Accessory):
	""" Motion homekit accessory """
	def __init__(self, **kwargs):
		""" Create motion accessory. Parameters : name(string), motion_detected(bool) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SENSOR, **kwargs)

		self.server = Server(name=kwargs.get("name","Motion sensor"), server_uuid=Server.UUID_MOTION_SENSOR)
		self.motion_detected = charact_bool_create (Charact.UUID_MOTION_DETECTED, Charact.PERM_RE, kwargs.get("motion_detected",False))
		self.server.add_charact(self.motion_detected)

		self.add_server(self.server)

	def set_motion_detected(self, value):
		""" Set the motion detected """
		self.motion_detected.set_value(value)

def main():
	""" Test """
	# Initialize homekit engine
	Homekit.init()

	# Create motion sensor
	sensor = MotionSensor(name="My motion sensor", motion_detected=False)

	# Create accessory
	Homekit.play(sensor)

	import time
	motion = False

	# Manage the motion (simple sample)
	while True:
		time.sleep(2)

		if motion is False:
			motion = True
		else:
			motion = False

		# Change the accessory motion
		sensor.set_motion_detected(motion)

if __name__ == "__main__":
	main()
