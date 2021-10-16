# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Manage the battery """
import machine
from tools import jsonconfig, useful

class BatteryConfig(jsonconfig.JsonConfig):
	""" Battery configuration """
	def __init__(self):
		""" Constructor """
		jsonconfig.JsonConfig.__init__(self)

		# Battery monitoring
		self.activated = False # Monitoring status
		self.level_gpio    = 12  # Monitoring GPIO
		self.full_battery  = 188 # 4.2V mesured with resistor 100k + 47k
		self.empty_battery = 158 # 3.6V mesured with resistor 100k + 47k

		# Force deep sleep if to many successive brown out reset detected
		self.brownout_detection = True
		self.brownout_count = 0

class Battery:
	""" Manage the battery information """
	config = None
	level = [-2]
	refresh = [0]

	@staticmethod
	def init():
		""" Init battery class """
		# If config not yet read
		if Battery.config is None:
			Battery.config = BatteryConfig()
			# If config failed to read
			if Battery.config.load() is False:
				# Write default config
				Battery.config.save()

	@staticmethod
	def get_level():
		""" Return the battery level between 0% to 100% (0%=3.6V 100%=4.2V).
			For the ESP32CAM with Gpio12, the value can be read only before the open of camera and SD card.
			The voltage always smaller than 1.5V otherwise the card does not boot (JTAG detection I think).
			This GPIO 12 of the ESP32CAM not have a pull up resistor, it is the only one which allows the ADC measurement.
			I had to patch the micropython firmware to be able to read the GPIO 12."""
		Battery.init()
		# If battery level not yet read at start
		if Battery.level[0] == -2:
			level = -1
			try:
				adc = machine.ADC(machine.Pin(Battery.config.level_gpio))
				adc.atten(machine.ADC.ATTN_11DB)
				adc.width(machine.ADC.WIDTH_9BIT)
				count = 3
				val = 0
				for i in range(count):
					val += adc.read()
				# If battery level pin not connected
				if val < (Battery.config.empty_battery * count) // 2:
					level = -1
				else:
					# Compute battery level
					level = Battery.calc_percent(val/count, Battery.config)
					if level < 0.:
						level = 0
					elif level > 100.:
						level = 100
					else:
						level = int(level)
				useful.syslog("Battery level %d %% (%d)"%(level, int(val/count)))
			except Exception as err:
				useful.syslog(err,"Cannot read battery status")
			Battery.level[0] = level
		return Battery.level[0]

	@staticmethod
	def is_activated():
		""" Indicates if the battery management activated """
		Battery.init()
		return Battery.config.activated

	@staticmethod
	def calc_percent(x, config):
		""" Calc the percentage of battery according to the configuration """
		x1 = config.full_battery
		y1 = 100
		x2 = config.empty_battery
		y2 = 0

		a = (y1 - y2)/(x1 - x2)
		b = y1 - (a * x1)
		y = a*x + b
		return y

	@staticmethod
	def protect():
		""" Protect the battery """
		Battery.init()
		Battery.keep_reset_cause()
		if Battery.manage_level() or Battery.is_too_many_brownout():
			useful.syslog("Sleep infinite")
			machine.deepsleep()

	@staticmethod
	def manage_level():
		""" Checks if the battery level is sufficient.
			If the battery is too low, we enter indefinite deep sleep to protect the battery """
		deepsleep = False
		if Battery.config.activated:
			# Can only be done once at boot before start the camera and sd card
			battery_level = Battery.get_level()

			# If the battery is too low
			if battery_level > 5 or battery_level < 0:
				battery_protect = False
			else:
				battery_protect = True

			# Case the battery has not enough current and must be protected
			if battery_protect:
				deepsleep = True
				useful.syslog("Battery too low %d %%"%battery_level)
		return deepsleep

	@staticmethod
	def keep_reset_cause():
		""" Keep reset cause """
		causes = {
			machine.PWRON_RESET     : "Power on",
			machine.HARD_RESET      : "Hard",
			machine.WDT_RESET       : "Watch dog",
			machine.DEEPSLEEP_RESET : "Deep sleep",
			machine.SOFT_RESET      : "Soft",
			machine.BROWNOUT_RESET  : "Brownout",
		}.setdefault(machine.reset_cause(), "%d"%machine.reset_cause())
		useful.syslog(" ")
		useful.syslog("%s Start %s"%('-'*10,'-'*10), display=False)
		useful.syslog("%s reset"%causes)

	@staticmethod
	def is_too_many_brownout():
		""" Checks the number of brownout reset """
		deepsleep = False

		if Battery.config.is_changed():
			Battery.config.load()

		if Battery.config.brownout_detection:
			# If the reset can probably due to insufficient battery
			if machine.reset_cause() == machine.BROWNOUT_RESET:
				Battery.config.brownout_count += 1
			else:
				Battery.config.brownout_count = 0

			Battery.config.save()

			# if the number of consecutive brownout resets is too high
			if Battery.config.brownout_count > 32:
				# Battery too low, save the battery status
				useful.syslog("Too many successive brownout reset")
				deepsleep = True
		return deepsleep

	@staticmethod
	def manage(resetBrownout=False):
		""" Manage the battery level duration """
		if Battery.refresh[0] % 10 == 0:
			if Battery.config.is_changed():
				Battery.config.load()
		Battery.refresh[0] += 1

		if resetBrownout:
			if Battery.config.brownout_detection:
				if Battery.config.brownout_count > 0:
					Battery.config.brownout_count = 0
					Battery.config.save()
