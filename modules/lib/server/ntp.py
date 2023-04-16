# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Manage server class """
import time
import wifi.wifi
import uasyncio
import server.server
import server.timesetting
import tools.logger
import tools.region
import tools.tasking

class Ntp:
	""" Internal clock synchronization """
	region_config = None
	server_config = None
	last_sync = 0

	@staticmethod
	def init():
		""" Initialise time synchronisation """
		if Ntp.region_config is None:
			Ntp.region_config = tools.region.RegionConfig()
			Ntp.region_config.load_create()
			server.timesetting.set_time(Ntp.region_config.current_time)
		else:
			Ntp.region_config.refresh()

		if Ntp.server_config is None:
			Ntp.server_config = server.server.ServerConfig()
			Ntp.server_config.load_create()
		else:
			Ntp.server_config.refresh()

	@staticmethod
	async def synchronize():
		""" Synchronize time """
		updated = False
		tools.logger.syslog("Synchronize time")

		# Try many time
		for i in range(3):
			# Keep old date
			old_time = time.time()

			# Read date from ntp server
			current_time = server.timesetting.set_date(Ntp.region_config.offset_time, dst=Ntp.region_config.dst, display=False)

			# If date get
			if current_time > 0:
				# Save new date
				Ntp.region_config.current_time = int(current_time)
				Ntp.region_config.save()

				# If clock changed
				if abs(old_time - current_time) > 1:
					# Log difference
					tools.logger.syslog("Time synchronized delta=%ds"%(current_time-old_time))
				updated = True
				break
			else:
				await uasyncio.sleep(1)
		return updated

	@staticmethod
	async def task(**kwargs):
		""" Internal clock synchronization task """
		Ntp.init()

		# If ntp synchronization enabled
		if Ntp.server_config.ntp:
			# If the wan is present
			if wifi.wifi.Wifi.is_wan_available():
				if Ntp.last_sync + 10799 < time.time() or Ntp.last_sync == 0:
					if await Ntp.synchronize():
						Ntp.last_sync = time.time()
						wifi.wifi.Wifi.wan_connected()
					else:
						wifi.wifi.Wifi.wan_disconnected()

		if Ntp.region_config.current_time + 599 < time.time():
			Ntp.region_config.current_time = time.time()
			Ntp.region_config.save()
		await uasyncio.sleep(307)

	@staticmethod
	def start():
		""" Start time synchronisation task """
		Ntp.init()
		if Ntp.server_config.ntp:
			tools.tasking.Tasks.create_monitor(Ntp.task)
		else:
			tools.logger.syslog("Ntp synchronization disabled in config")
