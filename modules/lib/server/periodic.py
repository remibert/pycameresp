# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Periodic task, get wanip, synchronize time """
from server import *
from server.user import *
from server.wanip import *
from server.timesetting import *
from server.wanip import *
from tools import jsonconfig,useful
import uasyncio
import wifi
import time

async def periodicTask():
	""" Detect the presence of occupants of the housing and automatically suspend the detection (ping the ip of occupants smartphones) """
	periodic = Periodic()
	await useful.taskMonitoring(periodic.task)
 
class Periodic:
	""" Class to manage periodic task """
	def __init__(self):
		""" Constructor """
		self.config = server.ServerConfig()
		self.config.load()
		self.wanip = None
		self.onePerDay = 0

	async def synchronizeTime(self):
		""" Synchronize time """
		result = False
		if self.config.ntp:
			for i in range(3):
				oldTime = time.time()
				currentTime = setDate(self.config.offsettime, dst=self.config.dst, display=False)
				if currentTime > 0:
					result = True
					self.config.currentTime = int(currentTime)
					self.config.save()
					if abs(oldTime - currentTime) > 5:
						useful.logError("Time synchronized")
					break
				else:
					await uasyncio.sleep(1)
		return result

	def isOnePerDay(self):
		""" Indicates if the action must be done on per day """
		date = useful.dateToBytes()[:14]
		if self.onePerDay == None or (date[:-2] == b"12" and date != self.onePerDay):
			self.onePerDay = date
			return True
		return False

	async def synchronizeWanip(self, forced):
		""" Synchronize wan ip """
		newWanip = await getWanIpAsync()
		if newWanip != None:
			if self.wanip != newWanip or forced:
				if self.config.notify:
					await useful.notifyMessage("Wan ip is %s"%newWanip)
			self.wanip = newWanip

	async def checkLogin(self):
		""" Inform that login detected """
		login =  User.getLoginState()
		if login != None:
			message = "Login %s detected"%("success" if login else "failed")
			if self.config.notify:
				await useful.notifyMessage(message, display=False)

	async def noWan(self):
		""" Treatment if no wan connected """
		if wifi.Station.isActivated():
			if wifi.Station.chooseNetwork(True, maxRetry=5000) == True:
				if wifi.AccessPoint.isActive() and wifi.AccessPoint.isActivated() == False:
					wifi.AccessPoint.stop()

	async def task(self):
		""" Periodic task method """
		pollingId = 0
		while True:
			if self.config.isChanged():
				useful.logError("Change server config %s"%self.config.toString(), display=False)
				self.config.load()

			if wifi.Station.isActive():
				if pollingId % 600 == 0:
					await self.synchronizeTime()

				if pollingId % 3600 == 0:
					forced = self.isOnePerDay()
					await self.synchronizeWanip(forced)
	
				if pollingId % 3 == 0:
					await self.checkLogin()
			else:
				if pollingId % 600 == 0:
					await self.noWan()
			await uasyncio.sleep(1)
			pollingId += 1
