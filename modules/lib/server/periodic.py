# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Periodic task, get wanip, synchronize time """
from server.server import ServerConfig, Server
from server.notifier import Notifier
from tools import jsonconfig,useful,battery
import uasyncio
import time

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
		self.wanip = None
		self.onePerDay = None
		self.getWanip = None
		self.setDate  = None
		self.getLoginState = None
		self.station = None

	def isOnePerDay(self):
		""" Indicates if the action must be done on per day """
		date = useful.dateToBytes()[:14]
		if self.onePerDay == None or (date[-2:] == b"12" and date != self.onePerDay):
			self.onePerDay = date
			return True
		return False

	async def synchronizeWanip(self, forced):
		""" Synchronize wan ip """
		if self.getWanip == None:
			from server.wanip import getWanIpAsync
			self.getWanip = getWanIpAsync
		if self.station == None:
			from wifi.station import Station
			self.station = Station
		newWanip = await self.getWanip()
		if newWanip != None:
			if self.wanip != newWanip or forced:
				if self.serverConfig.notify:
					await Notifier.notify("Lan Ip %s, Wan Ip %s"%(Station.getInfo()[0],newWanip))
			self.wanip = newWanip

	async def checkLogin(self):
		""" Inform that login detected """
		if self.getLoginState == None:
			from server.user import User
			self.getLoginState = User.getLoginState
		login =  self.getLoginState()
		if login != None:
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
					await self.synchronizeWanip(forced)
	
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
		while True:
			if self.serverConfig.isChanged():
				self.serverConfig.load()
			await self.manageNetwork(pollingId)

			await uasyncio.sleep(1)
			battery.Battery.manageAwake()
			pollingId += 1
