# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET

# Sample of temperature sensor
from homekit import *

def temperature():
	# Create the temperature characteristic
	temp = Charact(Charact.UUID_CURRENT_TEMPERATURE, Charact.PERM_READ | Charact.PERM_EVENT, Charact.TYPE_FLOAT, 0.0)
	temp.setConstraints(0.0,100.0)
	temp.setStep(0.1)
	temp.setUnit(Charact.UNIT_CELSIUS)

	# Create the name of server
	name      = Charact(Charact.UUID_NAME, Charact.PERM_READ, Charact.TYPE_STRING, "My temperature")

	# Create server
	server = Server(Server.UUID_TEMPERATURE_SENSOR)
	
	# Add all characteristics to the server
	server.addCharact(name)
	server.addCharact(temp)

	# Create accessory
	accessory = Accessory(Accessory.CID_SENSOR, name="PSE", manufacturer="Bertholet", model="Esp32", serial_number="061234567", fw_rev="1.2.3", hw_rev="4.5.6", product_vers="7.8")
	
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
	
	import time
	temperature = 0.0
	
	# Manage the temperature (simple sample)
	while True:
		time.sleep(2)
		
		temperature += 1.0:
		if temperature > 100.0
			temperature = 0.0
		
		# Change the accessory temperature 
		temp.setValue(temperature)
