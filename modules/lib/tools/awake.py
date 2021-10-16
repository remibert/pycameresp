# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Manage the battery """
import machine
import esp32
from tools import jsonconfig, useful

class AwakeConfig(jsonconfig.JsonConfig):
	""" Awake configuration """
	def __init__(self):
		""" Constructor """
		jsonconfig.JsonConfig.__init__(self)

		# GPIO wake up
		self.activated = False  # Wake up on GPIO status
		self.wake_up_gpio = 13 # Wake up GPIO number
		self.awake_duration = 120 # Awake duration in seconds
		self.sleep_duration = 3600*24*365 # Sleep duration in seconds

class Awake:
	""" Manage the awake """
	config = None
	awake_counter = [0] # Decrease each second
	refresh_counter = [0]

	@staticmethod
	def init():
		""" Init awake class """
		# If config not yet read
		if Awake.config is None:
			Awake.config = AwakeConfig()
			# If config failed to read
			if Awake.config.load() is False:
				# Write default config
				Awake.config.save()
		Awake.keep_awake()

	@staticmethod
	def set_pin_wake_up():
		""" Configure the wake up gpio on high level. For ESP32CAM, the GPIO 13 is used to detect the state of PIR detector. """
		Awake.init()
		try:
			if Awake.config.wake_up_gpio != 0:
				wake1 = machine.Pin(Awake.config.wake_up_gpio, mode=machine.Pin.IN, pull=machine.Pin.PULL_DOWN)
				esp32.wake_on_ext0(pin = wake1, level = esp32.WAKEUP_ANY_HIGH)
				useful.syslog("Pin wake up on %d"%Awake.config.wake_up_gpio)
			else:
				useful.syslog("Pin wake up disabled")
			return True
		except Exception as err:
			useful.syslog(err,"Cannot set wake up")
		return False

	@staticmethod
	def is_pin_wake_up():
		""" Indicates that the machine wake up on pin modification (Only available at start) """
		Awake.init()
		if Awake.config.activated:
			try:
				pin = machine.Pin(Awake.config.wake_up_gpio, machine.Pin.IN, machine.Pin.PULL_UP)
				return True if pin.value() == 1 else False
			except:
				return False
		else:
			return False

	@staticmethod
	def keep_awake():
		""" Keep awake  """
		if Awake.config.activated:
			Awake.awake_counter[0] = Awake.config.awake_duration

	@staticmethod
	def manage():
		""" Manage the awake duration """
		if Awake.refresh_counter[0] % 10 == 0:
			if Awake.config.is_changed():
				Awake.config.load()
		Awake.refresh_counter[0] += 1

		if Awake.config.activated:
			Awake.awake_counter[0] -= 1
			if Awake.awake_counter[0] <= 0:
				useful.syslog("Sleep %d s"%Awake.config.sleep_duration)

				# Set the wake up on PIR detection
				Awake.set_pin_wake_up()
				machine.deepsleep(Awake.config.sleep_duration*1000)
