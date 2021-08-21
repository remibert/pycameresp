# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Periodic task, wifi management, get wanIp, synchronize time """
from server.server import ServerConfig, Server
from tools import useful,battery
import wifi
import uasyncio

async def periodicTask():
	""" Periodic task """
	periodic = Periodic()
	await useful.taskMonitoring(periodic.task)

class Periodic:
	""" Class to manage periodic task """
	def __init__(self):
		""" Constructor """
		self.serverConfig = ServerConfig()
		self.serverConfig.load()
		self.getLoginState = None
		useful.WatchDog.start(useful.SHORT_WATCH_DOG)

	async def checkLogin(self):
		""" Inform that login detected """
		# Login state not yet get
		if self.getLoginState is None:
			from server.user import User
			self.getLoginState = User.getLoginState

		# Get login state
		login =  self.getLoginState()

		# If login detected
		if login is not None:
			from server.notifier import Notifier
			# If notification must be send
			if self.serverConfig.notify:
				message = b"Login %s detected"%(b"success" if login else b"failed")
				await Notifier.notify(message, display=False)

	async def task(self):
		""" Periodic task method """
		pollingId = 0
		
		useful.WatchDog.start(useful.SHORT_WATCH_DOG)
		while True:
			# Reload server config if changed
			if self.serverConfig.isChanged():
				self.serverConfig.load()

			# Manage server
			await Server.manage(pollingId)

			# Manage login user
			if pollingId % 5 == 0:
				await self.checkLogin()

			# Manage awake duration
			battery.Battery.manageAwake(wifi.Wifi.isWanConnected())

			# Reset watch dog
			useful.WatchDog.feed()
			await uasyncio.sleep(1)
			pollingId += 1
