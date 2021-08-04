# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Presence detection (determine if an occupant is present in the house) """
import uasyncio
import time
from tools import useful, jsonconfig
import wifi
from server.ping import asyncPing
from server.notifier import Notifier
from server.server import Server

class PresenceConfig(jsonconfig.JsonConfig):
	""" Configuration class of presence detection """
	def __init__(self):
		jsonconfig.JsonConfig.__init__(self)
		# Indicates if the presence detection is activated
		self.activated = False

		# Ip addresses of smartphones
		self.smartphones = [b"",b"",b"",b"",b""]

		# Notify presence
		self.notify = True

class Presence:
	""" Presence detection of smartphones """
	ABSENCE_TIMEOUT   = 15.*60.
	NO_ANSWER_TIMEOUT = 10.*60.
	FAST_POLLING      = 2.
	SLOW_POLLING      = 1.*60.

	PING_TIMEOUT      = 0.5
	PING_COUNT        = 4

	detected = [False]

	@staticmethod
	def isDetected():
		""" Indicates if presence detected """
		return Presence.detected[0]

	@staticmethod
	def setDetection(state):
		""" Force presence detection """
		Presence.detected[0] = state

	@staticmethod
	def init():
		""" Initialize the task """
		Presence.readConfig = 0.
		Presence.pollingDuration = Presence.FAST_POLLING
		Presence.config = PresenceConfig()
		
		Presence.activated = None
		Presence.lastTime = 0
		Presence.detected[0] = False

	@staticmethod
	async def task():
		""" Run the task """
		# If configuration must be read
		if Presence.config:
			if Presence.config.isChanged():
				if Presence.config.load() == False:
					Presence.config.save()
				useful.logError("Change presence config %s"%Presence.config.toString(), display=False)

		if Presence.config.activated == True and wifi.Station.isActive():
			presents = []
			currentDetected = None
			smartphoneInList = False

			for smartphone in Presence.config.smartphones:
				# If smartphone present
				if smartphone != b"":
					smartphoneInList = True

					# Ping smartphone
					sent,received,success = await asyncPing(smartphone, count=Presence.PING_COUNT, timeout=Presence.PING_TIMEOUT, quiet=True)
				
					# If a response received from smartphone
					if received > 0:
						presents.append(smartphone)
						print("%s %s detected"%(useful.dateToString()[12:], useful.tostrings(smartphone)))
						Presence.lastTime = time.time()
						currentDetected = True

			# If no smartphones detected during a very long time
			if Presence.lastTime + Presence.ABSENCE_TIMEOUT < time.time():
				# Nobody in the house
				currentDetected = False

			# If smartphone detected
			if currentDetected == True:
				# If no smartphone previously detected
				if Presence.isDetected() != currentDetected:
					# Notify the house is not empty
					msg = b""
					for present in presents:
						msg += b"%s "%present
					if Presence.config.notify:
						await Notifier.notify(b"Presence of %s"%(msg))
					Presence.setDetection(True)
			# If no smartphone detected
			elif currentDetected == False:
				# If smartphone previously detected
				if Presence.isDetected() != currentDetected:
					# Notify the house in empty
					if Presence.config.notify:
						await Notifier.notify(b"Empty house")
					Presence.setDetection(False)

			# If all smartphones not responded during a long time
			if Presence.lastTime + Presence.NO_ANSWER_TIMEOUT < time.time() and smartphoneInList == True:
				if Presence.pollingDuration != Presence.FAST_POLLING:
					print("%s fast polling"%(useful.dateToString()[12:]))
				# Set fast polling rate
				Presence.pollingDuration = Presence.FAST_POLLING
			else:
				if Presence.pollingDuration != Presence.SLOW_POLLING:
					print("%s slow polling"%(useful.dateToString()[12:]))
				# Reduce polling rate
				Presence.pollingDuration = Presence.SLOW_POLLING
		else:
			Presence.pollingDuration = Presence.SLOW_POLLING
			Presence.setDetection(False)

		# If the presence detection change
		if Presence.activated != Presence.config.activated:
			if Presence.config.notify:
				await Notifier.notify(b"Presence detection %s"%(b"on" if Presence.config.activated else b"off"))
			Presence.activated = Presence.config.activated

		# Wait before new ping
		await Server.waitResume(Presence.pollingDuration)
		return True

async def detectPresence():
	""" Detect the presence of occupants of the housing and automatically suspend the detection (ping the ip of occupants smartphones) """
	Presence.init()
	await useful.taskMonitoring(Presence.task)