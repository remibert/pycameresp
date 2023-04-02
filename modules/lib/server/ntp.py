# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Manage server class """
import time
import wifi
import uasyncio
from server import server, timesetting
from tools import logger,region,tasking

class Ntp:
	""" Internal clock synchronization """
	region_config = None
	server_config = None
	last_sync = 0

	@staticmethod
	def init():
		""" Initialise time synchronisation """
		if Ntp.region_config is None:
			Ntp.region_config = region.RegionConfig()
			Ntp.region_config.load_create()
			timesetting.set_time(Ntp.region_config.current_time)
		else:
			Ntp.region_config.refresh()

		if Ntp.server_config is None:
			Ntp.server_config = server.ServerConfig()
			Ntp.server_config.load_create()
		else:
			Ntp.server_config.refresh()

	@staticmethod
	async def synchronize():
		""" Synchronize time """
		updated = False
		logger.syslog("Synchronize time")

		# Try many time
		for i in range(3):
			# Keep old date
			oldTime = time.time()

			# Read date from ntp server
			current_time = timesetting.set_date(Ntp.region_config.offset_time, dst=Ntp.region_config.dst, display=False)

			# If date get
			if current_time > 0:
				# Save new date
				Ntp.region_config.current_time = int(current_time)
				Ntp.region_config.save()

				# If clock changed
				if abs(oldTime - current_time) > 1:
					# Log difference
					logger.syslog("Time synchronized delta=%ds"%(current_time-oldTime))
				updated = True
				break
			else:
				await uasyncio.sleep(1)
		if updated:
			wifi.Wifi.wan_connected()
		else:
			wifi.Wifi.wan_disconnected()
		return updated

	@staticmethod
	async def task(**kwargs):
		""" Internal clock synchronization task """
		polling = 13
		Ntp.init()

		# If ntp synchronization enabled
		if Ntp.server_config.ntp:
			# If the wan is present
			if wifi.Wifi.is_wan_available():
				if Ntp.last_sync + 21601 < time.time() or Ntp.last_sync == 0:
					if await Ntp.synchronize():
						Ntp.last_sync = time.time()
						polling = 607
		else:
			polling = 59

		if Ntp.region_config.current_time + 599 < time.time():
			Ntp.region_config.current_time = time.time()
			Ntp.region_config.save()
		await uasyncio.sleep(polling)

	@staticmethod
	def start():
		""" Start time synchronisation task """
		Ntp.init()
		if Ntp.server_config.ntp:
			tasking.Tasks.create_monitor(Ntp.task)
		else:
			logger.syslog("Ntp synchronization disabled in config")
