# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Presence detection (determine if an occupant is present in the house) """
import uasyncio
import time
from tools import useful, jsonconfig
import server
import wifi

class PresenceConfig:
	""" Configuration class of presence detection """
	def __init__(self):
		# Indicates if the presence detection is activated
		self.activated = False

		# Ip addresses of smartphones
		self.smartphones = [b"",b"",b"",b"",b""]

		# Notify presence
		self.notify = True

	def save(self, file = None):
		""" Save configuration """
		result = jsonconfig.save(self, file)
		return result

	def update(self, params):
		""" Update configuration """
		result = jsonconfig.update(self, params)
		return result

	def load(self, file = None):
		""" Load configuration """
		result = jsonconfig.load(self, file)
		return result

presenceDetected = False

def isPresenceDetected():
	""" Indicates if presence detected """
	global presenceDetected
	return presenceDetected

async def detectPresence():
	""" Detect the presence of occupants of the housing and automatically suspend the detection (ping the ip of occupants smartphones) """
	from server import notifyMessage, asyncPing
	from tools.useful import dateToString, dateToBytes

	global presenceDetected
	lastDetection = 0
	
	ABSENCE_TIMEOUT   = 15.*60.
	NO_ANSWER_TIMEOUT = 10.*60.
	FAST_POLLING      = 2.
	SLOW_POLLING      = 1.*60.

	PING_TIMEOUT      = 0.5
	PING_COUNT        = 4

	readConfig = 0.
	pollingDuration = FAST_POLLING
	config = None
	activated = None

	while 1:
		# If configuration must be read
		if readConfig <= 0.:
			config = PresenceConfig()
			config.load()
			readConfig = SLOW_POLLING
		else:
			readConfig -= pollingDuration

		if config.activated == True and wifi.Station.isActive():
			presents = []
			currentDetected = None
			smartphoneInList = False

			for smartphone in config.smartphones:
				# If smartphone present
				if smartphone != b"":
					smartphoneInList = True

					# Ping smartphone
					sent,received,success = await asyncPing(smartphone, count=PING_COUNT, timeout=PING_TIMEOUT, quiet=True)
				
					# If a response received from smartphone
					if received > 0:
						presents.append(smartphone)
						print("%s %s detected"%(useful.dateToString()[12:], useful.tostrings(smartphone)))
						lastDetection = time.time()
						currentDetected = True

			# If no smartphones detected during a very long time
			if lastDetection + ABSENCE_TIMEOUT < time.time():
				# Nobody in the house
				currentDetected = False

			# If smartphone detected
			if currentDetected == True:
				# If no smartphone previously detected
				if presenceDetected != currentDetected:
					# Notify the house is not empty
					msg = b""
					for present in presents:
						msg += b"%s "%present
					if config.notify:
						await notifyMessage(b"presence of %s"%(msg))
					presenceDetected = True
			# If no smartphone detected
			elif currentDetected == False:
				# If smartphone previously detected
				if presenceDetected != currentDetected:
					# Notify the house in empty
					if config.notify:
						await notifyMessage(b"empty house")
					presenceDetected = False

			# If all smartphones not responded during a long time
			if lastDetection + NO_ANSWER_TIMEOUT < time.time() and smartphoneInList == True:
				if pollingDuration != FAST_POLLING:
					print("%s fast polling"%(useful.dateToString()[12:]))
				# Set fast polling rate
				pollingDuration = FAST_POLLING
			else:
				if pollingDuration != SLOW_POLLING:
					print("%s slow polling"%(useful.dateToString()[12:]))
				# Reduce polling rate
				pollingDuration = SLOW_POLLING
		else:
			pollingDuration = SLOW_POLLING
			presenceDetected = False

		# If the presence detection change
		if activated != config.activated:
			if config.notify:
				await notifyMessage(b"presence detection %s"%(b"on" if config.activated else b"off"))
			activated = config.activated

		# Wait before new ping
		await server.waitResume(pollingDuration)


