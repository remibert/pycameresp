# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Miscellaneous utility functions """
import machine
from tools import useful

LONG_WATCH_DOG=15*60*1000
SHORT_WATCH_DOG=5*60*1000

class WatchDog:
	""" Watch dog timer """
	watchdog = None
	@staticmethod
	def start(timeout=LONG_WATCH_DOG):
		""" Start watch dog """
		WatchDog.watchdog  = machine.WDT(0, timeout)

	@staticmethod
	def feed():
		""" Feed the WDT """
		if WatchDog.watchdog:
			WatchDog.watchdog.feed()

class Inactivity:
	""" Class to manage inactivity timer """
	def __init__(self, callback, duration=LONG_WATCH_DOG, timer_id=-1):
		""" Inactivity timer constructor """
		self.timer = machine.Timer(timer_id)
		self.duration = duration
		self.callback = callback
		self.timer_id = timer_id
		self.start()

	def __del__(self):
		""" Destructor """
		self.stop()

	def start(self):
		""" Restart inactivity timer """
		self.timer.init(period=self.duration, mode=machine.Timer.ONE_SHOT, callback=self.callback)

	def stop(self):
		""" Stop timer """
		self.timer.deinit()

	def restart(self):
		""" Restart timer """
		self.stop()
		self.start()

async def task_monitoring(task):
	""" Check if task crash, log message and reboot if it too frequent """
	import uasyncio
	retry = 0
	lastError = ""

	while retry < 40:
		try:
			while True:
				if await task():
					retry = 0

		except Exception as err:
			lastError = useful.syslog(err, "Task error")
			retry += 1
			await uasyncio.sleep_ms(6000)
		useful.syslog("Task retry %d"%retry)
	useful.syslog("Too many task error reboot")

	from server.server import ServerConfig
	from server.notifier import Notifier

	config = ServerConfig()
	config.load()
	if config.notify:
		from tools import lang
		await Notifier.notify(lang.reboot_after_many%useful.tobytes(lastError))
	useful.reboot()
