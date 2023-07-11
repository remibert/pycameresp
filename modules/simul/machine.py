# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Simulate machine module """
PWRON_RESET = 1
HARD_RESET = 2
WDT_RESET = 3
DEEPSLEEP_RESET = 4
SOFT_RESET = 5
BROWNOUT_RESET = 6

def freq(a=0):
	""" Processor frequency """
	return 240*1000000

def reset_cause():
	""" Reset cause"""
	# return PWRON_RESET
	return BROWNOUT_RESET

def reset():
	""" Reset """

def deepsleep(duration=0):
	""" Deep sleep """

def lightsleep(duration=0):
	""" Light sleep """

class ADC:
	""" ADC """
	ATTN_11DB = 1
	WIDTH_9BIT = 9

	def __init__(self, pin):
		""" Constructor """
		self.pin = pin

	def atten(self, val):
		""" Atten """

	def width(self, val):
		""" Width """

	def read(self):
		""" Read """
		return 191

class Pin:
	""" Pin """
	WAKEUP_ANY_HIGH = 1
	IN = 1
	OUT = 1
	PULL_UP = 1
	PULL_DOWN =0
	IRQ_RISING = 2
	IRQ_FALLING = 4
	def __init__(self, *args, **params):
		""" Constructor """
		self.handler = None
		self.trigger = None
		self.val = 0

	def value(self, val=None):
		""" Value """
		if val is not None:
			self.val = val
		return self.val

	def on(self):
		""" On """

	def off(self):
		""" Off"""

	def irq(self, handler=None, trigger=None):
		""" Irq """
		self.handler = handler
		self.trigger = trigger

class Timer:
	""" Timer """
	ONE_SHOT = 0
	PERIODIC = 1
	def __init__(self, period=5000, mode=0, callback=None):
		""" Constructor """
		self.timer = None

	def init(self, mode=0, period=- 1, callback=None):
		""" Init """
		import threading
		if self.timer:
			self.timer.cancel()

		self.timer = threading.Timer(period/1000., callback)
		self.timer.start()

	def deinit(self):
		""" Deinit """
		if self.timer:
			self.timer.cancel()

class WDT:
	""" Watchdog class """
	def __init__(self, id_, duration):
		""" Constructor """

	def feed(self):
		""" Feed watch dog"""

class RTC:
	""" Real time clock """
	def datetime(self, current_date):
		""" Date time """
		return None
class SDCard:
	""" Sd card """
	# pylint:disable=redefined-outer-name
	def __init__(self, slot=1, width=1, cd=None, wp=None, sck=None, miso=None, mosi=None, cs=None, freq=1):
		pass

class Counter:
	""" See https://github.com/micropython/micropython/pull/6639 for the PCNT Counter. """
	UP = 1
	def __init__(self, a, src, direction):
		""" Constructor """
		self.val = 0
	def pause(self):
		""" Pause """
	def value(self, val=None):
		""" Get value """
		if val is not None:
			self.val += val
		return self.val
	def resume(self):
		""" Resume """
	def deinit(self):
		""" Stops the Counter """
	def filter_ns(self, value):
		""" Filter nano seconds """

class I2S:
	""" I2S simulation """
	TX = 0
	STEREO = 0

	def write(self, buffer):
		""" Write buffer """

	def deinit(self):
		""" Deinit """

class UART:
	""" Uart simulation """
	def __init__(self, uart=1, baudrate=9600, rx=0, tx=0):
		""" Create uart simulation """
		self.uart = uart
		self.rx = rx
		self.tx = tx
		self.reception = b""
		self.sent = b""

	def simul_receive(self, buffer):
		""" Simulate receive """
		self.reception = buffer

	def write(self, buffer):
		""" Write buffer on uart """
		self.sent = buffer

	def close(self):
		""" Close uart """

	def read(self, length):
		""" Read buffer """
		if len(self.reception) >= length:
			result = self.reception[0:length]
			self.reception = self.reception[length:]
		else:
			result = self.reception
			self.reception = b""
		return result

	def readinto(self, buffer):
		""" Read buffer from uart """
		if len(self.reception) > 0:
			i = 0
			for char in self.reception:
				buffer[i] = char
				i += 1
			self.reception = b""

	def any(self):
		""" Return the length received """
		return len(self.reception)
