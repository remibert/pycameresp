# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
PWRON_RESET = 1
HARD_RESET = 2
WDT_RESET = 3
DEEPSLEEP_RESET = 4
SOFT_RESET = 5
BROWNOUT_RESET = 6

def freq(a):
	return 240*1000000

def reset_cause():
	# return PWRON_RESET
	return BROWNOUT_RESET

def reset():
	pass

def deepsleep(duration=0):
	pass
	
class ADC:
	ATTN_11DB = 1
	WIDTH_9BIT = 9

	def __init__(self, pin):
		self.pin = pin

	def atten(self, val):
		pass

	def width(self, val):
		pass
	
	def read(self):
		return 191
		
class Pin:
	WAKEUP_ANY_HIGH = 1
	IN = 1
	OUT = 1
	PULL_UP = 1
	def __init__(self, *args, **params):
		pass
	
	def value(self, val=0):
		return val

class Timer:
	ONE_SHOT = 0
	PERIODIC = 1
	def __init__(self, ident):
		self.timer = None
		
	def init(self, mode=0, period=- 1, callback=None):
		import threading
		if self.timer:
			self.timer.cancel()
		
		self.timer = threading.Timer(period/1000., callback)
		self.timer.start()
	
	def deinit(self):
		if self.timer:
			self.timer.cancel()