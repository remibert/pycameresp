# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET

# Sample of homekit fan
from homekit import *

def fan():
	# Create characteristic toggle on
	on        = Charact(Charact.UUID_ON,                 Charact.PERM_RWE,  Charact.TYPE_BOOL,   True)

	# Create characteristic name
	name      = Charact(Charact.UUID_NAME,               Charact.PERM_READ, Charact.TYPE_STRING, "Mon ventilo")

	# Create characteristic direction
	direction = Charact(Charact.UUID_ROTATION_DIRECTION, Charact.PERM_RWE,  Charact.TYPE_INT,    1)
	direction.setConstraints(0,1)
	direction.setStep(1)

	def onCallbackRead(self):
		print("onCallbackRead")
		# Be careful the characteristic passed in parameter is the internal C implementation, not python class Charact

	def onCallbackWrite(self):
		# Be careful the characteristic passed in parameter is the internal C implementation, not python class Charact
		if self.get_value():
			self.set_value(False)
		else:
			self.set_value(True)

	# Register callback on read
	on.setReadCallback(onCallbackRead)
	
	# Register callback on write
	on.setWriteCallback(onCallbackWrite)

	# Create server
	server = Server(Server.UUID_FAN)

	# Add all characteristics to the server
	server.addCharact(name)
	server.addCharact(on)
	server.addCharact(direction)

	# Create accessory
	accessory = Accessory(Accessory.CID_FAN, name="PSE", manufacturer="Bertholet", model="Esp32", serial_number="061234567", fw_rev="1.2.3", hw_rev="4.5.6", product_vers="7.8")

	# Set product data
	accessory.setProductData("REMIBERT")

	# Add server to accessory
	accessory.addServer(server)

	# Create homekit
	Homekit.init()

	# Initialize setup code (format must be 'xxx-xx-xxx')
	Homekit.setSetupCode("111-11-111")

	# Initialize setup id (length must be 4 bytes)
	Homekit.setSetupId("BERT")

	# Add accessory to homekit
	Homekit.addAccessory(accessory)
	
	# Start homekit
	Homekit.start()

