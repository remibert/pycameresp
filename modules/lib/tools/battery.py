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
		self.activated = False
		self.levelGpio  = 12
		self.wakeUpGpio = 13
		self.fullBattery  = 191 # 4.2V mesured with resistor 100k + 47k
		self.emptyBattery = 161 # 3.6V mesured with resistor 100k + 47k

class Battery:
	config = None
	level = [-2]
	""" Manage the battery information """

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
				print("Battery level %d %% (%d)"%(level, int(val/count)))
			except:
				print("Cannot read battery status")
			Battery.level[0] = level
		return Battery.level[0]

	@staticmethod
	def isActivated():
		""" Indicates if the battery management activated """
		Battery.init()
		return Battery.config.activated

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
			print("Cannot set wake up")
		return False

	@staticmethod
	def isPinWakeUp():
		""" Indicates that the machine wake up on pin modification (Only available at start) """
		Battery.init()
		try:
			pin = machine.Pin(Battery.config.wakeUpGpio, machine.Pin.IN, machine.Pin.PULL_UP)
			return True if pin.value() == 1 else False
		except:
			return False

	@staticmethod
	def protect():
		""" Checks if the battery level is sufficient, and checks the number of brownout reset. 
			If the battery is too low, we enter indefinite deep sleep to protect the battery """
		# Can only be done once at boot before start the camera and sd card
		batteryLevel = Battery.getLevel()

		# If the battery is too low
		if batteryLevel > 5:
			batteryProtect = False
		# If the battery level can't be read
		elif batteryLevel < 0:
			# If the reset is due to insufficient battery
			if machine.reset_cause() == machine.BROWNOUT_RESET:
				batteryProtect = True
			else:
				batteryProtect = False
		else:
			batteryProtect = True

		brownoutCounter = 0
		# If the reset can probably due to insufficient battery
		if machine.reset_cause() == machine.BROWNOUT_RESET:
			try:
				file = open("brownout.txt","r")
				val = file.read()
				brownoutCounter = int(val) + 1
			except Exception as err:
				print(useful.exception(err))

		try:
			file = open("brownout.txt","w")
			file.write("%d"%brownoutCounter)
			file.flush()
			file.close()
		except Exception as err:
			print(useful.exception(err))

		# If the battery level seems sufficient
		if batteryProtect == False:
			# if the number of consecutive brownout resets is too high
			if brownoutCounter > 10:
				# Battery too low, save the battery status
				file = open("battery.txt","w")
				file.write("Too many brownout reset with battery level at %d %%"%batteryLevel)
				file.flush()
				file.close()
				batteryProtect = True

		# Case the battery has not enough current and must be protected
		if batteryProtect:
			print("#####################################")
			print("# DEEP SLEEP TO PROTECT THE BATTERY #")
			print("#####################################")
			machine.deepsleep()
		else:
			# Set the wake up on PIR detection
			Battery.setPinWakeUp()
