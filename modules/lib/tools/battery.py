# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Manage the battery """
from tools import jsonconfig
from tools import useful

try: import machine
except: pass
try:import esp32
except:pass

class BatteryConfig(jsonconfig.JsonConfig):
	""" Battery configuration """
	def __init__(self):
		""" Constructor """
		jsonconfig.JsonConfig.__init__(self)

		# Battery monitoring
		self.monitoring = False # Monitoring status
		self.levelGpio    = 12  # Monitoring GPIO
		self.fullBattery  = 191 # 4.2V mesured with resistor 100k + 47k
		self.emptyBattery = 161 # 3.6V mesured with resistor 100k + 47k

		# GPIO wake up
		self.wakeUp = False  # Wake up on GPIO status
		self.wakeUpGpio = 13 # Wake up GPIO number
		self.awakeTime = 120 # Awake time on battery (seconds)

		# Force deep sleep if to many successive brown out reset detected
		self.brownoutDetection = True
		self.brownoutCount = 0


class Battery:
	""" Manage the battery information """
	config = None
	level = [-2]
	awakeCounter = [0] # Decrease each second

	@staticmethod
	def init():
		""" Init battery class """
		# If config not yet read
		if Battery.config == None:
			Battery.config = BatteryConfig()
			# If config failed to read
			if Battery.config.load() == False:
				# Write default config
				Battery.config.save()
		Battery.keepAwake()

	@staticmethod
	def getLevel():
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
				adc = machine.ADC(machine.Pin(Battery.config.levelGpio))
				adc.atten(machine.ADC.ATTN_11DB)
				adc.width(machine.ADC.WIDTH_9BIT)
				count = 3
				val = 0
				for i in range(count):
					val += adc.read()
				level = Battery.calcPercent(val/count, Battery.config)
				if level < 0.:
					level = 0
				elif level > 100.:
					level = 100
				else:
					level = int(level)
				useful.logError("Battery level %d %% (%d)"%(level, int(val/count)))
			except Exception as err:
				useful.logError("Cannot read battery status",err)
			Battery.level[0] = level
		return Battery.level[0]

	@staticmethod
	def isActivated():
		""" Indicates if the battery management activated """
		Battery.init()
		return Battery.config.monitoring

	@staticmethod
	def calcPercent(x, config):
		""" Calc the percentage of battery according to the configuration """
		x1 = config.fullBattery
		y1 = 100
		x2 = config.emptyBattery
		y2 = 0

		a = (y1 - y2)/(x1 - x2)
		b = y1 - (a * x1)
		y = a*x + b
		return y

	@staticmethod
	def setPinWakeUp():
		""" Configure the wake up gpio on high level. For ESP32CAM, the GPIO 13 is used to detect the state of PIR detector. """
		Battery.init()
		try:
			wake1 = machine.Pin(Battery.config.wakeUpGpio, mode = machine.Pin.IN)
			esp32.wake_on_ext0(pin = wake1, level = esp32.WAKEUP_ANY_HIGH)
			return True
		except Exception as err:
			useful.logError("Cannot set wake up",err)
		return False

	@staticmethod
	def isPinWakeUp():
		""" Indicates that the machine wake up on pin modification (Only available at start) """
		Battery.init()
		if Battery.config.wakeUp:
			try:
				pin = machine.Pin(Battery.config.wakeUpGpio, machine.Pin.IN, machine.Pin.PULL_UP)
				return True if pin.value() == 1 else False
			except:
				return False
		else:
			return False

	@staticmethod
	def protect():
		""" Protect the battery """
		Battery.init()
		Battery.keepResetCause()
		if Battery.manageLevel() or Battery.manageBrownout():
			machine.deepsleep()

	@staticmethod
	def manageLevel():
		""" Checks if the battery level is sufficient. 
			If the battery is too low, we enter indefinite deep sleep to protect the battery """
		deepsleep = False
		if Battery.config.monitoring:
			# Can only be done once at boot before start the camera and sd card
			batteryLevel = Battery.getLevel()

			# If the battery is too low
			if batteryLevel > 5:
				batteryProtect = False
			# If the battery level can't be read
			elif batteryLevel <= 0:
				batteryProtect = False
			else:
				batteryProtect = True

			# Case the battery has not enough current and must be protected
			if batteryProtect:
				deepsleep = True
				useful.logError("Battery too low %d %%"%batteryLevel)
		return deepsleep

	@staticmethod
	def keepResetCause():
		""" Keep reset cause """
		causes = {
			machine.PWRON_RESET     : "Power on",
			machine.HARD_RESET      : "Hard",
			machine.WDT_RESET       : "Watch dog",
			machine.DEEPSLEEP_RESET : "Deep sleep",
			machine.SOFT_RESET      : "Soft",
			machine.BROWNOUT_RESET  : "Brownout",
		}.setdefault(machine.reset_cause(), "%d"%machine.reset_cause())
		useful.logError("%s reset"%causes)

	@staticmethod
	def clearBrownout():
		""" If network connection successful, the brownout can counter can be cleared """
		if Battery.config.brownoutDetection:
			Battery.config.brownoutCount = 0
			Battery.config.save()

	@staticmethod
	def manageBrownout():
		""" Checks the number of brownout reset """
		deepsleep = False

		if Battery.config.brownoutDetection:
			# If the reset can probably due to insufficient battery
			if machine.reset_cause() == machine.BROWNOUT_RESET:
				Battery.config.brownoutCount += 1
			else:
				Battery.config.brownoutCount = 0

			Battery.config.save()

			# if the number of consecutive brownout resets is too high
			if Battery.config.brownoutCount > 32:
				# Battery too low, save the battery status
				useful.logError("Too many successive brownout reset")
				deepsleep = True
		return deepsleep

	@staticmethod
	def keepAwake():
		""" Keep awake  """
		if Battery.config.wakeUp:
			Battery.awakeCounter[0] = Battery.config.awakeTime

	@staticmethod
	def manageAwake():
		""" Manage the awake duration """
		if Battery.config.wakeUp:
			Battery.awakeCounter[0] -= 1
			if Battery.awakeCounter[0] < 0:
				useful.logError("Sleeping")
				# Set the wake up on PIR detection
				Battery.setPinWakeUp()
				machine.deepsleep()