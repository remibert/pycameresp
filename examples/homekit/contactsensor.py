# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Contact homekit accessory """
from homekit import *

class ContactSensor(Accessory):
	""" Contact homekit accessory """
	def __init__(self, **kwargs):
		""" Create contact accessory. Parameters : name(string), contact_detected(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SENSOR, **kwargs)

		self.server = Server(name=kwargs.get("name","Contact sensor"), server_uuid=Server.UUID_CONTACT_SENSOR)
		self.contact_detected = charact_uint8_create (Charact.UUID_CONTACT_SENSOR_STATE, Charact.PERM_RE, kwargs.get("contact_detected",0))
		self.contact_detected.set_constraint(0, 1, 1)
		self.server.add_charact(self.contact_detected)

		self.add_server(self.server)

	def set_contact_detected(self, value):
		""" Set the contact detected """
		self.contact_detected.set_value(value)

def main():
	""" Test """
	# Initialize homekit engine
	Homekit.init()

	# Create contact sensor
	sensor = ContactSensor(name="My contact sensor", contact_detected=0)

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
		sensor.set_contact_detected(contact)

if __name__ == "__main__":
	main()
