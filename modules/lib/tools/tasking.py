# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Miscellaneous utility functions """
import machine
from tools import strings,logger,system,watchdog

class Inactivity:
	""" Class to manage inactivity timer """
	def __init__(self, callback, duration=watchdog.LONG_WATCH_DOG, timer_id=-1):
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
	memory_error_count = 0
	max_retry = 20
	try:
		while retry < max_retry:
			try:
				while True:
					if await task():
						retry = 0
			except MemoryError as err:
				lastError = logger.syslog(err, "Memory error")
				from gc import collect
				collect()
				memory_error_count += 1
				if memory_error_count > 10:
					logger.syslog("Too many memory error")
					break
				retry += 1
				await uasyncio.sleep_ms(6000)
			except Exception as err:
				lastError = logger.syslog(err, "Task error")
				retry += 1
				await uasyncio.sleep_ms(6000)
			logger.syslog("Task retry %d/%d"%(retry,max_retry))
		logger.syslog("Too many task error reboot")

		from server.server import ServerConfig
		from server.notifier import Notifier

		config = ServerConfig()
		config.load()
		from tools import lang
		await Notifier.notify(lang.reboot_after_many%strings.tobytes(lastError), enabled=config.notify)
	finally:
		system.reboot()
