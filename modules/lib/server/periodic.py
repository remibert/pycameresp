# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Periodic task, get wanIp, synchronize time """
from server.server import ServerConfig, Server
from server.notifier import Notifier
from tools import useful,battery
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
		self.wanIp = None
		self.onePerDay = None
		self.getWanIpAsync = None
		self.setDate  = None
		self.getLoginState = None
		self.station = None
		self.serverPostponed = None
		useful.WatchDog.start(useful.SHORT_DURATION)

	def isOnePerDay(self):
		""" Indicates if the action must be done on per day """
		date = useful.dateToBytes()[:14]
		if self.onePerDay is None or (date[-2:] == b"12" and date != self.onePerDay):
			self.onePerDay = date
			return True
		return False

	async def synchronizeWanIp(self, forced):
		""" Synchronize wan ip """
		if Server.isWanConnected():
			if self.getWanIpAsync is None:
				from server.wanip import getWanIpAsync
				self.getWanIpAsync = getWanIpAsync
			if self.station is None:
				from wifi.station import Station
				self.station = Station
			try:
				newWanIp = None
				newWanIp = await self.getWanIpAsync()
			except Exception as err:
				useful.logError("Cannot get wan ip", err)
			if newWanIp is not None:
				from tools.battery import Battery
				Battery.clearBrownout()
				if self.wanIp != newWanIp or forced:
					if self.serverConfig.notify:
						await Notifier.notify("Lan Ip %s, Wan Ip %s, %s"%(self.station.getInfo()[0],newWanIp, useful.uptime()))
				self.wanIp = newWanIp

	async def checkLogin(self):
		""" Inform that login detected """
		if self.getLoginState is None:
			from server.user import User
			self.getLoginState = User.getLoginState
		login =  self.getLoginState()
		if login is not None:
			message = "Login %s detected"%("success" if login else "failed")
			if self.serverConfig.notify:
				await Notifier.notify(message, display=False)

	async def manageNetwork(self, pollingId):
		""" Manage the start postponed of network """
		if Server.isWifiStarted():
			if Server.isWanConnected():
				if pollingId % 3600 == 0:
					await Server.synchronizeTime()

				forced =  self.isOnePerDay()
				if pollingId % 3600 == 0 or forced:
					await self.synchronizeWanIp(forced)

				if pollingId % 4 == 0:
					await self.checkLogin()
			else:
				if pollingId % 600 == 0:
					await Server.manage()
		else:
			if self.serverPostponed == 0:
				await Server.manage()
			else:
				self.serverPostponed -= 1

	async def task(self):
		""" Periodic task method """
		self.serverPostponed = self.serverConfig.serverPostponed
		pollingId = 0
		useful.WatchDog.start(useful.SHORT_DURATION)
		while True:
			if self.serverConfig.isChanged():
				self.serverConfig.load()
			await self.manageNetwork(pollingId)

			await uasyncio.sleep(1)
			battery.Battery.manageAwake()
			pollingId += 1
			useful.WatchDog.feed()
