# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
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
	def __init__(self, *args, **params):
		""" Constructor """

	def value(self, val=0):
		""" Value """
		return val

	def on(self):
		""" On """

	def off(self):
		""" Off"""
class Timer:
	""" Timer """
	ONE_SHOT = 0
	PERIODIC = 1
	def __init__(self, ident):
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
	def datetime(self, date_):
		""" Date time """
		return None
class SDCard:
	""" Sd card """
