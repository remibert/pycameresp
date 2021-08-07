# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from tools import jsonconfig,useful
import wifi
import uasyncio
import time

class ServerConfig(jsonconfig.JsonConfig):
	""" Servers configuration """
	def __init__(self):
		jsonconfig.JsonConfig.__init__(self)
		self.ntp = True
		self.ftp = True
		self.http = True
		self.telnet = True
		self.offsettime = 1
		self.dst = True
		self.currentTime = 0
		self.notify = True
		self.serverPostponed = 10

class ServerContext:
	""" Context to initialize the servers """
	def __init__(self, loop=None, pageLoader=None, preload=False, withoutServer=False, httpPort=80):
		from server.timesetting import setTime
		self.loop          = loop
		self.pageLoader    = pageLoader
		self.preload       = preload
		self.withoutServer = withoutServer
		self.httpPort      = httpPort
		self.wifiStarted   = False
		self.wanConnected  = False
		self.serverStarted = False
		self.config        = ServerConfig()
		self.setDate = None
		if self.config.load() == False:
			self.config.save()
		setTime(self.config.currentTime)

class Server:
	""" Class used to manage the servers """
	suspended = [False]
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
	async def waitResume(duration=None):
		""" Wait the resume of task servers """
		if duration != None:
			Server.tasks[id(uasyncio.current_task())] = True
			await uasyncio.sleep(duration)
		if Server.suspended[0]:
			Server.tasks[id(uasyncio.current_task())] = True
			while Server.suspended[0]:
				await uasyncio.sleep(1)
		Server.tasks[id(uasyncio.current_task())] = False

	@staticmethod
	def isAllWaiting():
		""" Check if all task resumed """
		result = True
		for key, value in Server.tasks.items():
			if value == False:
				result = False
		return result

	@staticmethod
	async def waitAllSuspended():
		""" Wait all servers suspended """
		for i in range(150):
			if Server.isAllWaiting() == True:
				break
			else:
				if i % 30 == 0:
					print("Wait all servers suspended...")
				await uasyncio.sleep(0.1)
				useful.WatchDog.feed()

	@staticmethod
	def isWifiStarted():
		""" Indicates if the wifi is started """
		return Server.context.wifiStarted

	@staticmethod
	def isWanConnected():
		""" Indicates if the wan is connected """
		return wifi.Station.isConnected()

	@staticmethod
	def init(loop=None, pageLoader=None, preload=False, withoutServer=False, httpPort=80):
		""" Init servers
		loop : asyncio loop
		pageLoader : callback to load html page
		preload : True force the load of page at the start, 
		False the load of page is done a the first http connection (Takes time on first connection) """
		Server.context = ServerContext(loop, pageLoader, preload, withoutServer, httpPort)
		useful.logError("%s Start %s"%('-'*10,'-'*10), display=False)
		useful.logError(useful.sysinfo(display=False))

		from server.periodic import periodicTask
		loop.create_task(periodicTask())

	@staticmethod
	async def synchronizeTime():
		""" Synchronize time """
		result = False
		if Server.context.config.ntp:
			if Server.isWanConnected():
				if Server.context.setDate == None:
					from server.timesetting import setDate
					Server.context.setDate = setDate
				for i in range(3):
					oldTime = time.time()
					currentTime = Server.context.setDate(Server.context.config.offsettime, dst=Server.context.config.dst, display=False)
					if currentTime > 0:
						result = True
						Server.context.config.currentTime = int(currentTime)
						Server.context.config.save()

						from tools.battery import Battery
						Battery.clearBrownout()

						if abs(oldTime - currentTime) > 0:
							useful.logError("Time synchronized delta=%ds"%(currentTime-oldTime))
						break
					else:
						await uasyncio.sleep(1)
		return result

	@staticmethod
	async def connectNetwork():
		""" Connect the network """
		flush = False
		# If wifi not started
		if Server.context.wifiStarted == False:
			Server.context.wifiStarted = True
			forceAccessPoint = False
			# If wifi station connected
			if await wifi.Station.start():
				flush = True
				Server.context.wanConnected = True
			else:
				# If wifi station enabled
				if wifi.Station.isActivated():
					# Fall back on access point
					forceAccessPoint = True

			# Start access point and force it if no wifi station connected
			wifi.AccessPoint.start(forceAccessPoint)
		
		# If wifi station not connected
		if Server.context.wanConnected == False:
			# If wifi connected
			if await wifi.Station.chooseNetwork(True, maxRetry=5) == True:
				Server.context.wanConnected = True
				flush = True
				# If access point forced 
				if wifi.AccessPoint.isActive() and wifi.AccessPoint.isActivated() == False:
					wifi.AccessPoint.stop()

		# If flush of message required
		if flush:
			from server.notifier import Notifier
			# Add notifier if no notifier registered
			if Notifier.isEmpty():
				from server.pushover import notifyMessage
				Notifier.add(notifyMessage)
			await Notifier.flush()
			await Server.synchronizeTime()

	@staticmethod
	async def startServer():
		""" Start all servers """
		# If server not started
		if Server.context.serverStarted == False:
			# If wifi available
			if Server.context.wifiStarted:
				Server.context.serverStarted = True
				config = Server.context.config

				# If telnet activated
				if config.telnet and Server.context.withoutServer == False:
					# Load and start telnet
					import server.telnet
					server.telnet.start()

				# If ftp activated
				if config.ftp and Server.context.withoutServer == False:
					# Load and start ftp server
					import server.ftpserver
					server.ftpserver.start(loop=Server.context.loop, preload=Server.context.preload)

				# If http activated
				if config.http and Server.context.withoutServer == False:
					# Load and start http server
					import server.httpserver
					server.httpserver.start(loop=Server.context.loop, loader=Server.context.pageLoader, preload=Server.context.preload, port=Server.context.httpPort, name="httpServer")

					# If camera present
					if useful.iscamera():
						# Load and start streaming http server
						server.httpserver.start(loop=Server.context.loop, loader=Server.context.pageLoader, preload=Server.context.preload, port=Server.context.httpPort +1, name="StreamingServer")

				from server.presence import detectPresence
				Server.context.loop.create_task(detectPresence())

	@staticmethod
	async def manage():
		""" Manage the network and server """
		await Server.connectNetwork()
		await Server.startServer()