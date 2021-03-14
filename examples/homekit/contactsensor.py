# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from homekit import *

class ContactSensor(Accessory):
	""" Contact homekit accessory """
	def __init__(self, **kwargs):
		""" Create contact accessory. Parameters : name(string), contactDetected(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SENSOR, **kwargs)

		self.server = Server(name=kwargs.get("name","Contact sensor"), serverUuid=Server.UUID_CONTACT_SENSOR)
		self.contactDetected = charactUint8Create (Charact.UUID_CONTACT_SENSOR_STATE, Charact.PERM_RE, kwargs.get("contactDetected",0))
		self.contactDetected.setConstraint(0, 1, 1)
		self.server.addCharact(self.contactDetected)

		self.addServer(self.server)
	
	def setContactDetected(self, value):
		""" Set the contact detected """
		self.contactDetected.setValue(value)

def main():
	# Initialize homekit engine
	Homekit.init()

	# Create contact sensor
	sensor = ContactSensor(name="My contact sensor", contactDetected=0)
	
	# Create accessory
	Homekit.play(sensor)

	import time
	contact = 0

	# Manage the contact (simple sample)
	while True:
		time.sleep(2)
		
		if contact == 0:
			contact = 1
		else:
			contact = 0

		# Change the accessory contact 
		sensor.setContactDetected(contact)

if __name__ == "__main__":
	main()