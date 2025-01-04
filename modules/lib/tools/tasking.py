# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Miscellaneous utility functions """
import time
import uasyncio
import machine
import tools.lang
import tools.strings
import tools.logger
import tools.system
import tools.watchdog
import tools.info
import tools.topic

class Inactivity:
	""" Class to manage inactivity timer """
	def __init__(self, callback, duration=tools.watchdog.LONG_WATCH_DOG, timer_id=-1):
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

class ServerInstance:
	""" Abstract class for implementing an asynchronous server task """
	def __init__(self, **kwargs):
		""" Constructor """
		self.kwargs = kwargs

	async def on_connection(self, reader, writer):
		""" Method called when connecting to the server """

	def start(self):
		""" Start server """
		name    = self.kwargs.get("name","Unknown")
		host    = self.kwargs.get("host","0.0.0.0")
		port    = self.kwargs.get("port",0)
		backlog = self.kwargs.get("backlog",1)
		Tasks.loop.create_task(uasyncio.start_server(self.on_connection, host=host, port=port, backlog=backlog))
		return name, port

class ClientInstance:
	""" Abstract class for implementing an asynchronous client task """
	def __init__(self, **kwargs):
		""" Constructor """
		self.kwargs = kwargs

	def start(self):
		""" Start client """
		name    = self.kwargs.get("name","Unknown")
		port    = self.kwargs.get("port",0)
		return name, port

class Task:
	""" Asynchronous task informations """
	def __init__(self, name):
		""" Constructor """
		self.id = id(uasyncio.current_task())
		self.name = name
		self.status = False

class Tasks:
	""" Asynchronous task manager """
	loop           = None
	servers        = []
	clients        = []
	suspended      = [False]
	slow_time      = [0]
	slow_ratio     = [1]
	tasks          = {}
	tasknames      = {}
	started = False

	@staticmethod
	def init():
		""" Initialise tasks """
		if Tasks.loop is None:
			Tasks.loop = uasyncio.get_event_loop()

	@staticmethod
	def create_task(function):
		""" Create new asynchronous task """
		Tasks.init()
		Tasks.loop.create_task(function)
		return function

	@staticmethod
	def create_monitor(function, **kwargs):
		""" Create new asynchronous task with monitor """
		Tasks.init()
		Tasks.loop.create_task(Tasks.monitor(function, **kwargs))
		return function

	@staticmethod
	def create_server(server):
		""" Create server task """
		Tasks.init()
		Tasks.servers.append(server)

	@staticmethod
	def create_client(client):
		""" Create client task """
		Tasks.init()
		Tasks.clients.append(client)

	@staticmethod
	def start_all():
		""" Start all servers and clients """
		if Tasks.started is False:
			Tasks.started = True
			for server in Tasks.servers:
				name, port = server.start()
				tools.logger.syslog("%s port:%d"%(name, port))
			for client in Tasks.clients:
				name, port = client.start()
				tools.logger.syslog("%s port:%d"%(name, port))

	@staticmethod
	def run():
		""" Run all asynchronous tasks """
		try:
			# Run asyncio for ever
			Tasks.loop.run_forever()
		except KeyboardInterrupt:
			tools.logger.syslog("Ctr-C in main")
		except Exception as err:
			tools.logger.syslog(err)
			tools.system.reboot("Crash in main")

	@staticmethod
	async def monitor(task, **kwargs):
		""" Check if task crash, log message and reboot if it too frequent """
		# import uasyncio
		retry = 0
		lastError = ""
		memory_error_count = 0
		max_retry = 20
		try:
			while retry < max_retry:
				try:
					while True:
						if await task(**kwargs):
							retry = 0
				except MemoryError as err:
					lastError = tools.logger.syslog(err, "Memory error, %s"%tools.strings.tostrings(tools.info.meminfo()))
					from gc import collect
					collect()
					memory_error_count += 1
					if memory_error_count > 10:
						tools.logger.syslog("Too many memory error")
						break
					retry += 1
					await uasyncio.sleep_ms(6000)
				except Exception as err:
					lastError = tools.logger.syslog(err, "Task error")
					retry += 1
					await uasyncio.sleep_ms(6000)
				tools.logger.syslog("Task retry %d/%d"%(retry,max_retry))
			tools.logger.syslog("Too many task error reboot")

			from server.server import ServerConfig
			from server.notifier import Notifier

			config = ServerConfig()
			config.load()
			Notifier.notify(topic=tools.topic.information, message=tools.lang.reboot_after_many%tools.strings.tobytes(lastError), enabled=config.notify)
			await uasyncio.sleep_ms(10000)
		except Exception as err:
			tools.logger.exception(err)
		finally:
			tools.system.reboot("Reboot due too many error")

	@staticmethod
	def suspend():
		""" Suspend the asyncio task of servers """
		Tasks.suspended[0] = True

	@staticmethod
	def resume():
		""" Resume the asyncio task of servers """
		Tasks.suspended[0] = False

	@staticmethod
	async def wait_resume(duration=None, name=""):
		""" Wait the resume of task servers """
		taskid = id(uasyncio.current_task())
		current = Tasks.tasks.get(taskid, None)
		if current is None:
			current = Task(name)
			Tasks.tasks[taskid] = current
		if duration is not None:
			current.status = True
			await uasyncio.sleep_ms(duration)
		if Tasks.suspended[0]:
			current.status = True
			while Tasks.suspended[0]:
				await uasyncio.sleep_ms(500)
		current.status = False

	@staticmethod
	def get_slow_ratio():
		""" Indicates that task other than server must be slower """
		if Tasks.slow_time[0] != 0:
			if time.time() > Tasks.slow_time[0]:
				Tasks.slow_time[0] = 0
				Tasks.slow_ratio[0] = 1
		return Tasks.slow_ratio[0]

	@staticmethod
	def is_slow_down():
		""" Indicates if in slow down mode """
		if time.time() < Tasks.slow_time[0]:
			return True
		return False

	@staticmethod
	def slow_down(duration=20, ratio=25):
		""" Set the state slow for a specified duration """
		keep = True

		if Tasks.slow_time[0] != 0:
			if Tasks.slow_ratio[0] > ratio:
				keep = False
				Tasks.slow_time[0] = time.time() + duration
		if keep:
			Tasks.slow_time[0] = time.time() + duration
			Tasks.slow_ratio[0] = ratio

	@staticmethod
	def is_all_waiting():
		""" Check if all task resumed """
		result = []
		for name, task in Tasks.tasks.items():
			if task.status is False:
				result.append(task.name)
		return result

	@staticmethod
	async def wait_all_suspended():
		""" Wait all servers suspended """
		for i in range(20):
			waiting = Tasks.is_all_waiting()
			if len(waiting) == 0:
				print("All servers suspended")
				break
			else:
				if i % 4 == 0:
					print("Wait for servers to suspend : %s"%str(waiting))
				await uasyncio.sleep(0.5)
				tools.watchdog.WatchDog.feed()
