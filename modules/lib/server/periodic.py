# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Periodic task, wifi management, get wanIp, synchronize time """
from server.server import ServerConfig, Server
from tools import battery, lang, awake, tasking
import wifi
import uasyncio

async def periodicTask():
	""" Periodic task """
	periodic = Periodic()
	await tasking.taskMonitoring(periodic.task)

class Periodic:
	""" Class to manage periodic task """
	def __init__(self):
		""" Constructor """
		self.serverConfig = ServerConfig()
		self.serverConfig.load()
		self.getLoginState = None
		tasking.WatchDog.start(tasking.SHORT_WATCH_DOG)

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
				if login:
					await Notifier.notify(lang.login_success_detected, display=False)
				else:
					await Notifier.notify(lang.login_failed_detected, display=False)

	async def task(self):
		""" Periodic task method """
		pollingId = 0
		
		tasking.WatchDog.start(tasking.SHORT_WATCH_DOG)
		while True:
			# Reload server config if changed
			if pollingId % 5 == 0:
				# Manage login user
				await self.checkLogin()

				if self.serverConfig.isChanged():
					self.serverConfig.load()

			# Manage server
			await Server.manage(pollingId)

			# Manage awake duration
			awake.Awake.manage()

			# Manage battery level
			battery.Battery.manage(wifi.Wifi.isWanConnected())

			# Reset watch dog
			tasking.WatchDog.feed()
			await uasyncio.sleep(1)
			pollingId += 1
