# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from homekit import *

class Thermostat(Accessory):
	OFF       = 0
	HEATING   = 1
	COOLING   = 2
	AUTOMATIC = 3
	""" Thermostat homekit accessory """
	def __init__(self, **kwargs):
		""" Create thermostat accessory. Parameters : name(string), currentState(int), targetState(int), temperature(float), targetTemperature(float), tempDispUnits(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_THERMOSTAT, **kwargs)
		self.server = Server(name=kwargs.get("name","Thermostat"), serverUuid=Server.UUID_THERMOSTAT)

		self.currentState = charactUint8Create (Charact.UUID_CURRENT_HEATING_COOLING_STATE, Charact.PERM_RE, kwargs.get("currentState",0))
		self.currentState.setConstraint(0, 2, 1)
		self.server.addCharact(self.currentState)

		self.targetState = charact = charactUint8Create (Charact.UUID_TARGET_HEATING_COOLING_STATE, Charact.PERM_RWE, kwargs.get("targetState",0))
		self.targetState.setConstraint(0, 3, 1)
		self.targetState.setWriteCallback(self.writeTargetState)
		self.server.addCharact(self.targetState)

		self.temperature = charactFloatCreate (Charact.UUID_CURRENT_TEMPERATURE, Charact.PERM_RE, kwargs.get("temperature",20.))
		self.temperature .setConstraint(0.0, 100.0, 0.1)
		self.temperature .setUnit(Charact.UNIT_CELSIUS)
		self.server.addCharact(self.temperature)

		self.targetTemperature = charactFloatCreate (Charact.UUID_TARGET_TEMPERATURE, Charact.PERM_RWE, kwargs.get("targetTemperature",10.))
		self.targetTemperature.setConstraint(10.0, 38.0, 0.1)
		self.targetTemperature.setUnit(Charact.UNIT_CELSIUS)
		self.targetTemperature.setWriteCallback(self.writeTargetTemperature)
		self.server.addCharact(self.targetTemperature)

		self.tempDispUnits = charactUint8Create (Charact.UUID_TEMPERATURE_DISPLAY_UNITS, Charact.PERM_RWE, kwargs.get("tempDispUnits",0))
		self.tempDispUnits.setConstraint(0, 1, 1)
		self.server.addCharact(self.tempDispUnits)

		self.coolingThreshold = charactFloatCreate (Charact.UUID_COOLING_THRESHOLD_TEMPERATURE, Charact.PERM_RWE, kwargs.get("coolingThreshold",20.))
		self.coolingThreshold.setConstraint(10.0, 38.0, 0.1)
		self.coolingThreshold.setUnit(Charact.UNIT_CELSIUS)
		self.coolingThreshold.setWriteCallback(self.writeCoolingThreshold)
		self.server.addCharact(self.coolingThreshold)

		self.heatingThreshold = charactFloatCreate (Charact.UUID_HEATING_THRESHOLD_TEMPERATURE, Charact.PERM_RWE, kwargs.get("heatingThreshold",22.))
		self.heatingThreshold.setConstraint(10.0, 38.0, 0.1)
		self.heatingThreshold.setUnit(Charact.UNIT_CELSIUS)
		self.heatingThreshold.setWriteCallback(self.writeHeatingThreshold)
		self.server.addCharact(self.heatingThreshold)
		
		self.currentHumidity = charactFloatCreate (Charact.UUID_CURRENT_RELATIVE_HUMIDITY, Charact.PERM_RE, kwargs.get("currHumidity",0.))
		self.currentHumidity.setConstraint(0.0, 100.0, 1.0)
		self.currentHumidity.setUnit(Charact.UNIT_PERCENTAGE)
		self.server.addCharact(self.currentHumidity)
		
		self.addServer(self.server)
		self.previousState = None

	def writeTargetState(self, value):
		self.targetState.setValue(value)

	def writeTargetTemperature(self, value):
		self.targetTemperature.setValue(value)

	def writeCoolingThreshold(self, value):
		self.coolingThreshold.setValue(value)

	def writeHeatingThreshold(self, value):
		self.heatingThreshold.setValue(value)
	
	def manage(self):
		# If command of self
		if self.previousState != self.targetState.getValue():
			self.previousState = self.targetState.getValue()
			if   self.targetState.getValue() == Thermostat.OFF:
				print("Force OFF")
				self.currentState.setValue(Thermostat.OFF)
			elif self.targetState.getValue() == Thermostat.HEATING:
				print("Force HEATING")
			elif self.targetState.getValue() == Thermostat.COOLING:
				print("Force COOLING")
			elif self.targetState.getValue() == Thermostat.AUTOMATIC:
				print("Force AUTOMATIC")
		
		newState = Thermostat.OFF
		if  self.targetState.getValue() == Thermostat.HEATING:
			if self.temperature.getValue() < self.targetTemperature.getValue():
				print("Start HEATING")
				newState = Thermostat.HEATING
			else:
				print("OFF")

		if  self.targetState.getValue() == Thermostat.COOLING:
			if self.temperature.getValue() > self.targetTemperature.getValue():
				print("Start COOLING")
				newState = Thermostat.COOLING
			else:
				print("OFF")

		if  self.targetState.getValue() == Thermostat.AUTOMATIC:
			if self.temperature.getValue() > self.coolingThreshold.getValue():
				print("Start COOLING")
				newState = Thermostat.COOLING
			elif self.temperature.getValue() < self.heatingThreshold.getValue():
				print("Start HEATING")
				newState = Thermostat.HEATING
			else:
				print("OFF")

		self.currentState.setValue(newState)
		return newState
		
	def setTemperature(self, temperature):
		self.temperature.setValue(temperature)
	
	def getTemperature(self):
		return self.temperature.getValue()

def main():
	# Initialize homekit engine
	Homekit.init()
	
	# Create accessory
	thermostat = Thermostat(name="My thermostat")
	Homekit.play(thermostat)
	import time
	
	while 1:
		# Manage thermostat
		state = thermostat.manage()
		
		# Temperature simulation
		temperature = thermostat.getTemperature()
		if   state == Thermostat.HEATING: temperature += 0.5
		elif state == Thermostat.COOLING: temperature -= 0.5
		
		# Set current temperature
		thermostat.setTemperature(temperature)
		print("Temperature %.1f"%temperature)
		
		time.sleep(1)

if __name__ == "__main__":
	main()