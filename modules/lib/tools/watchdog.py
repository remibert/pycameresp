# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Watchdog class """
import sys
import machine

LONG_WATCH_DOG=15*60*1000
SHORT_WATCH_DOG=5*60*1000

class WatchDog:
	""" Watch dog timer """
	watchdog = None
	current = 0
	max_duration = 0
	timer = None
	@staticmethod
	def start(timeout=LONG_WATCH_DOG):
		""" Start watch dog """
		WatchDog.max_duration = timeout
		WatchDog.current = 0

		# With pico pi RP2040 the max is 8.3s
		if sys.platform == "rp2" and timeout >  8388:
			WatchDog.timer =  machine.Timer(period=5000, mode=machine.Timer.PERIODIC, callback=WatchDog.extended_duration)
			WatchDog.watchdog  = machine.WDT(0, 6000)
		else:
			WatchDog.watchdog  = machine.WDT(0, timeout)

	@staticmethod
	def extended_duration(timer):
		""" Extends the tiny duration of the RP2 watchdog """
		if WatchDog.current < WatchDog.max_duration:
			WatchDog.current += 5000
			WatchDog.watchdog.feed()

	@staticmethod
	def feed():
		""" Feed the WDT """
		if WatchDog.watchdog:
			WatchDog.current = 0
			WatchDog.watchdog.feed()
