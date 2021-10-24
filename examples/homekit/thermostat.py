# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Thermostat homekit accessory """
from homekit import *
class Thermostat(Accessory):
	""" Thermostat homekit accessory """
	OFF       = 0
	HEATING   = 1
	COOLING   = 2
	AUTOMATIC = 3
	def __init__(self, **kwargs):
		""" Create thermostat accessory. Parameters : name(string), current_state(int), target_state(int), temperature(float), target_temperature(float), temp_disp_units(int) curr_humidity(float) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_THERMOSTAT, **kwargs)
		self.server = Server(name=kwargs.get("name","Thermostat"), server_uuid=Server.UUID_THERMOSTAT)

		self.current_state = charact_uint8_create (Charact.UUID_CURRENT_HEATING_COOLING_STATE, Charact.PERM_RE, kwargs.get("current_state",0))
		self.current_state.set_constraint(0, 2, 1)
		self.server.add_charact(self.current_state)

		self.target_state = charact = charact_uint8_create (Charact.UUID_TARGET_HEATING_COOLING_STATE, Charact.PERM_RWE, kwargs.get("target_state",0))
		self.target_state.set_constraint(0, 3, 1)
		self.server.add_charact(self.target_state)

		self.temperature = charact_float_create (Charact.UUID_CURRENT_TEMPERATURE, Charact.PERM_RE, kwargs.get("temperature",20.))
		self.temperature .set_constraint(0.0, 100.0, 0.1)
		self.temperature .set_unit(Charact.UNIT_CELSIUS)
		self.server.add_charact(self.temperature)

		self.target_temperature = charact_float_create (Charact.UUID_TARGET_TEMPERATURE, Charact.PERM_RWE, kwargs.get("target_temperature",10.))
		self.target_temperature.set_constraint(10.0, 38.0, 0.1)
		self.target_temperature.set_unit(Charact.UNIT_CELSIUS)
		self.server.add_charact(self.target_temperature)

		self.temp_disp_units = charact_uint8_create (Charact.UUID_TEMPERATURE_DISPLAY_UNITS, Charact.PERM_RWE, kwargs.get("temp_disp_units",0))
		self.temp_disp_units.set_constraint(0, 1, 1)
		self.server.add_charact(self.temp_disp_units)

		self.cooling_threshold = charact_float_create (Charact.UUID_COOLING_THRESHOLD_TEMPERATURE, Charact.PERM_RWE, kwargs.get("cooling_threshold",26.))
		self.cooling_threshold.set_constraint(10.0, 38.0, 0.1)
		self.cooling_threshold.set_unit(Charact.UNIT_CELSIUS)
		self.server.add_charact(self.cooling_threshold)

		self.heating_threshold = charact_float_create (Charact.UUID_HEATING_THRESHOLD_TEMPERATURE, Charact.PERM_RWE, kwargs.get("heating_threshold",18.))
		self.heating_threshold.set_constraint(10.0, 38.0, 0.1)
		self.heating_threshold.set_unit(Charact.UNIT_CELSIUS)
		self.server.add_charact(self.heating_threshold)

		self.current_humidity = charact_float_create (Charact.UUID_CURRENT_RELATIVE_HUMIDITY, Charact.PERM_RE, kwargs.get("curr_humidity",0.))
		self.current_humidity.set_constraint(0.0, 100.0, 1.0)
		self.current_humidity.set_unit(Charact.UNIT_PERCENTAGE)
		self.server.add_charact(self.current_humidity)

		self.add_server(self.server)
		self.previous_state = None

	def manage(self):
		""" Manage state """
		# If command of self
		if self.previous_state != self.target_state.get_value():
			self.previous_state = self.target_state.get_value()
			if   self.target_state.get_value() == Thermostat.OFF:
				print("Force OFF")
				self.current_state.set_value(Thermostat.OFF)
			elif self.target_state.get_value() == Thermostat.HEATING:
				print("Force HEATING")
			elif self.target_state.get_value() == Thermostat.COOLING:
				print("Force COOLING")
			elif self.target_state.get_value() == Thermostat.AUTOMATIC:
				print("Force AUTOMATIC")

		newState = Thermostat.OFF
		if  self.target_state.get_value() == Thermostat.HEATING:
			if self.temperature.get_value() < self.target_temperature.get_value():
				print("Start HEATING")
				newState = Thermostat.HEATING
			else:
				print("OFF")

		if  self.target_state.get_value() == Thermostat.COOLING:
			if self.temperature.get_value() > self.target_temperature.get_value():
				print("Start COOLING")
				newState = Thermostat.COOLING
			else:
				print("OFF")

		if  self.target_state.get_value() == Thermostat.AUTOMATIC:
			if self.temperature.get_value() > self.cooling_threshold.get_value():
				print("Start COOLING")
				newState = Thermostat.COOLING
			elif self.temperature.get_value() < self.heating_threshold.get_value():
				print("Start HEATING")
				newState = Thermostat.HEATING
			else:
				print("OFF")

		self.current_state.set_value(newState)
		return newState

	def set_temperature(self, temperature):
		""" Set temperature """
		self.temperature.set_value(temperature)

	def get_temperature(self):
		""" Get temperature """
		return self.temperature.get_value()

def main():
	""" Test """
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
		temperature = thermostat.get_temperature()
		if   state == Thermostat.HEATING:
			temperature += 0.5
		elif state == Thermostat.COOLING:
			temperature -= 0.5

		# Set current temperature
		thermostat.set_temperature(temperature)
		print("Temperature %.1f"%temperature)

		time.sleep(1)

if __name__ == "__main__":
	main()
 