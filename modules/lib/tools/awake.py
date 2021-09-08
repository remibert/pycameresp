# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Manage the battery """
from tools import jsonconfig, useful
import machine
import esp32

class AwakeConfig(jsonconfig.JsonConfig):
	""" Awake configuration """
	def __init__(self):
		""" Constructor """
		jsonconfig.JsonConfig.__init__(self)

		# GPIO wake up
		self.activated = False  # Wake up on GPIO status
		self.wakeUpGpio = 13 # Wake up GPIO number
		self.awakeDuration = 120 # Awake duration in seconds
		self.sleepDuration = 3600*24*365 # Sleep duration in seconds

class Awake:
	""" Manage the awake """
	config = None
	awakeCounter = [0] # Decrease each second
	refreshCounter = [0]

	@staticmethod
	def init():
		""" Init awake class """
		# If config not yet read
		if Awake.config == None:
			Awake.config = AwakeConfig()
			# If config failed to read
			if Awake.config.load() == False:
				# Write default config
				Awake.config.save()
		Awake.keepAwake()

	@staticmethod
	def setPinWakeUp():
		""" Configure the wake up gpio on high level. For ESP32CAM, the GPIO 13 is used to detect the state of PIR detector. """
		Awake.init()
		try:
			if Awake.config.wakeUpGpio != 0:
				wake1 = machine.Pin(Awake.config.wakeUpGpio, mode=machine.Pin.IN, pull=machine.Pin.PULL_DOWN)
				esp32.wake_on_ext0(pin = wake1, level = esp32.WAKEUP_ANY_HIGH)
				useful.syslog("Pin wake up on %d"%Awake.config.wakeUpGpio)
			else:
				useful.syslog("Pin wake up disabled")
			return True
		except Exception as err:
			useful.syslog(err,"Cannot set wake up")
		return False

	@staticmethod
	def isPinWakeUp():
		""" Indicates that the machine wake up on pin modification (Only available at start) """
		Awake.init()
		if Awake.config.activated:
			try:
				pin = machine.Pin(Awake.config.wakeUpGpio, machine.Pin.IN, machine.Pin.PULL_UP)
				return True if pin.value() == 1 else False
			except:
				return False
		else:
			return False

	@staticmethod
	def keepAwake():
		""" Keep awake  """
		if Awake.config.activated:
			Awake.awakeCounter[0] = Awake.config.awakeDuration

	@staticmethod
	def manage():
		""" Manage the awake duration """
		if Awake.refreshCounter[0] % 10 == 0:
			if Awake.config.isChanged():
				Awake.config.load()
		Awake.refreshCounter[0] += 1

		if Awake.config.activated:
			Awake.awakeCounter[0] -= 1
			if Awake.awakeCounter[0] <= 0:
				useful.syslog("Sleep %d s"%Awake.config.sleepDuration)

				# Set the wake up on PIR detection
				Awake.setPinWakeUp()
				machine.deepsleep(Awake.config.sleepDuration*1000)
