# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Manage server class """
import time
from video.video import Camera
import wifi
import uasyncio
from tools import jsonconfig,useful,builddate,lang, tasking

class ServerConfig(jsonconfig.JsonConfig):
	""" Servers configuration """
	def __init__(self):
		jsonconfig.JsonConfig.__init__(self)
		self.ntp = True
		self.ftp = True
		self.http = True
		self.telnet = True
		self.wanip = True
		self.notify = True
		self.server_postponed = 7

class ServerContext:
	""" Context to initialize the servers """
	def __init__(self, loop=None, page_loader=None, preload=False, http_port=80):
		from server.timesetting import set_time
		self.loop          = loop
		self.page_loader    = page_loader
		self.preload       = preload
		self.http_port      = http_port
		self.server_started = False
		self.notifier      = None
		self.get_wan_ip_async = None
		self.wan_ip = None
		self.server_config  = ServerConfig()
		self.region_config  = lang.RegionConfig()
		self.set_date = None
		self.one_per_day = None
		self.flushed = False

		if self.server_config.load() is False:
			self.server_config.save()

		if self.region_config.load() is False:
			self.region_config.save()

		self.server_postponed = self.server_config.server_postponed
		set_time(self.region_config.current_time)
class Server:
	""" Class used to manage the servers """
	suspended = [False]
	slow_speed = [None]
	tasks = {}
	context = None

	@staticmethod
	def suspend():
		""" Suspend the asyncio task of servers """
		Server.suspended[0] = True

	@staticmethod
	def resume():
		""" Resume the asyncio task of servers """
		Server.suspended[0] = False

	@staticmethod
	async def wait_resume(duration=None):
		""" Wait the resume of task servers """
		if duration is not None:
			Server.tasks[id(uasyncio.current_task())] = True
			await uasyncio.sleep(duration)
		if Server.suspended[0]:
			Server.tasks[id(uasyncio.current_task())] = True
			while Server.suspended[0]:
				await uasyncio.sleep(1)
		Server.tasks[id(uasyncio.current_task())] = False

	@staticmethod
	def is_slow():
		""" Indicates that task other than server must be slower """
		if Server.slow_speed[0] is None:
			return False
		elif time.time() > Server.slow_speed[0]:
			Server.slow_speed[0] = None
			return False
		else:
			return True

	@staticmethod
	def slow_down(duration=20):
		""" Set the state slow for a specified duration """
		Server.slow_speed[0] = time.time() + duration

	@staticmethod
	def is_all_waiting():
		""" Check if all task resumed """
		result = True
		for key, value in Server.tasks.items():
			if value is False:
				result = False
		return result

	@staticmethod
	async def wait_all_suspended():
		""" Wait all servers suspended """
		for i in range(30):
			if Server.is_all_waiting() is True:
				break
			else:
				if i % 6 == 0:
					print("Wait all servers suspended...")
				await uasyncio.sleep(0.5)
				tasking.WatchDog.feed()

	@staticmethod
	def init(loop=None, page_loader=None, preload=False, http_port=80):
		""" Init servers
		loop : asyncio loop
		page_loader : callback to load html page
		preload : True force the load of page at the start,
		False the load of page is done a the first http connection (Takes time on first connection) """
		Server.context = ServerContext(loop, page_loader, preload, http_port)
		useful.syslog(useful.sysinfo(display=False))
		useful.syslog("Firmware build date '%s'"%useful.tostrings(builddate.date))

		from server.periodic import periodic_task
		loop.create_task(periodic_task())

	@staticmethod
	async def synchronize_wan_ip(forced):
		""" Synchronize wan ip """
		# If wan ip synchronization enabled
		if Server.context.server_config.wanip:
			if wifi.Wifi.is_wan_available():
				useful.syslog("Synchronize Wan ip")
				# Wan ip not yet get
				if Server.context.get_wan_ip_async is None:
					from server.wanip import get_wan_ip_async
					Server.context.get_wan_ip_async = get_wan_ip_async

				# Get wan ip
				newWanIp = await Server.context.get_wan_ip_async()

				# If wan ip get
				if newWanIp is not None:
					# If wan ip must be notified
					if (Server.context.wan_ip != newWanIp or forced):
						await Server.context.notifier.notify("Lan Ip %s, Wan Ip %s, %s"%(wifi.Station.get_info()[0],newWanIp, useful.uptime()))
					Server.context.wan_ip = newWanIp
					wifi.Wifi.wan_connected()
				else:
					useful.syslog("Cannot get wan ip")
					wifi.Wifi.wan_disconnected()

	@staticmethod
	async def synchronize_time():
		""" Synchronize time """
		# If ntp synchronization enabled
		if Server.context.server_config.ntp:
			# If the wan is present
			if wifi.Wifi.is_wan_available():
				useful.syslog("Synchronize time")

				# If synchronisation not yet done
				if Server.context.set_date is None:
					from server.timesetting import set_date
					Server.context.set_date = set_date

				updated = False
				# Try many time
				for i in range(3):
					# Keep old date
					oldTime = time.time()

					# Read date from ntp server
					current_time = Server.context.set_date(Server.context.region_config.offset_time, dst=Server.context.region_config.dst, display=False)

					# If date get
					if current_time > 0:
						# Save new date
						Server.context.region_config.current_time = int(current_time)
						Server.context.region_config.save()

						# If clock changed
						if abs(oldTime - current_time) > 1:
							# Log difference
							useful.syslog("Time synchronized delta=%ds"%(current_time-oldTime))
						updated = True
						break
					else:
						await uasyncio.sleep(1)
				if updated:
					wifi.Wifi.wan_connected()
				else:
					wifi.Wifi.wan_disconnected()

	@staticmethod
	def is_one_per_day():
		""" Indicates if the action must be done on per day """
		date = useful.date_to_bytes()[:14]
		if Server.context.one_per_day is None or (date[-2:] == b"12" and date != Server.context.one_per_day):
			Server.context.one_per_day = date
			return True
		return False

	@staticmethod
	async def start_server():
		""" Start all servers """
		# If server not started
		if Server.context.server_started is False:
			# If wifi available
			if wifi.Wifi.is_lan_connected():
				Server.context.server_started = True

				# Add notifier if no notifier registered
				if Server.context.notifier.is_empty():
					from server.pushover import notify_message
					Server.context.notifier.add(notify_message)

				# If telnet activated
				if Server.context.server_config.telnet:
					# Load and start telnet
					import server.telnet
					server.telnet.start()

				# If ftp activated
				if Server.context.server_config.ftp:
					# Load and start ftp server
					import server.ftpserver
					server.ftpserver.start(loop=Server.context.loop, preload=Server.context.preload)

				# If http activated
				if Server.context.server_config.http:
					# Load and start http server
					import server.httpserver
					server.httpserver.start(loop=Server.context.loop, loader=Server.context.page_loader, preload=Server.context.preload, port=Server.context.http_port, name="httpServer")

					# If camera present
					if useful.iscamera() and Camera.is_activated():
						# Load and start streaming http server
						server.httpserver.start(loop=Server.context.loop, loader=Server.context.page_loader, preload=Server.context.preload, port=Server.context.http_port +1, name="StreamingServer")

				from server.presence import detect_presence
				Server.context.loop.create_task(detect_presence())

	@staticmethod
	async def manage(polling_id):
		""" Manage the network and server """
		# Server can be started
		if Server.context.server_postponed == 0:
			# Start server if no yet started
			await Server.start_server()

			# Polling for wifi
			if polling_id %179 == 0:
				await wifi.Wifi.manage()

			# Polling for notification not sent
			if polling_id %181 == 0 and Server.context.flushed is False:
				if wifi.Wifi.is_wan_available():
					await Server.synchronize_time()
					await Server.context.notifier.flush()
					if wifi.Wifi.is_wan_connected():
						Server.context.flushed = True

			# Polling for time synchronisation
			if polling_id % 3607 == 0:
				await Server.synchronize_time()

			# Polling for get wan ip
			if polling_id % 59 == 0:
				forced =  Server.is_one_per_day()
			else:
				forced = False

			if polling_id % 3593 == 0 or forced:
				await Server.synchronize_wan_ip(forced)

			# Save current time
			if polling_id % 59 == 0:
				Server.context.region_config.current_time = time.time()
				Server.context.region_config.save()
		else:
			Server.context.server_postponed -= 1

			# If server can start
			if Server.context.server_postponed == 0:
				from server.notifier import Notifier
				Server.context.notifier = Notifier

				# Start wifi
				await wifi.Wifi.manage()

				# If wan connected
				if wifi.Wifi.is_wan_available():
					# Synchronize time
					await Server.synchronize_time()

					# Flush notification not sent
					await Server.context.notifier.flush()
					if wifi.Wifi.is_wan_connected():
						Server.context.flushed = True
