# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Periodic task, wifi management, get wan_ip, synchronize time """
import gc
import uasyncio
import server.user
import server.server
import wifi.wifi
import tools.lang
import tools.tasking
import tools.watchdog
import tools.info
import tools.system
import tools.support
import tools.topic
import tools.builddate
import tools.filesystem
if tools.support.battery():
	import tools.battery

class Periodic:
	""" Class to manage periodic task """
	server_config = None

	@staticmethod
	def init():
		""" Constructor """
		if Periodic.server_config is None:
			Periodic.server_config = server.server.ServerConfig()
			Periodic.server_config.load_create()
			Periodic.last_notif = None
			Periodic.current_time = 0
			tools.watchdog.WatchDog.start(tools.watchdog.SHORT_WATCH_DOG)
		else:
			Periodic.server_config.refresh()

	@staticmethod
	async def check_login():
		""" Inform that login detected """
		# Get login state
		login =  server.user.User.get_login_state()

		# If login detected
		if login is not None:
			from server.notifier import Notifier
			if login:
				if Periodic.last_notif is None:
					notif = True
					Periodic.last_notif = Periodic.current_time
				elif Periodic.last_notif + 5*60 < Periodic.current_time:
					Periodic.last_notif = Periodic.current_time
					notif = True
				else:
					notif = False
				if notif:
					Notifier.notify(topic=tools.topic.login, value=tools.topic.value_success, message=tools.lang.login_success_detected, display=False, enabled=Periodic.server_config.notify)
			else:
				Notifier.notify    (topic=tools.topic.login, value=tools.topic.value_failed,  message=tools.lang.login_failed_detected,  display=False, enabled=Periodic.server_config.notify)

	@staticmethod
	async def task(**kwargs):
		""" Periodic task method """
		Periodic.init()
		if tools.filesystem.ismicropython():
			STEP = 5
		else:
			STEP = 1

		polling_id = 0

		tools.watchdog.WatchDog.start(tools.watchdog.SHORT_WATCH_DOG)
		while True:
			# Reload server config if changed
			if polling_id % (2*STEP) == 0:
				# Manage login user
				await Periodic.check_login()
				Periodic.server_config.refresh()

				# Manage server
				if wifi.wifi.Wifi.is_lan_connected():
					tools.tasking.Tasks.start_all()

				# # Reset brownout counter if wifi connected
				if wifi.wifi.Wifi.is_wan_connected():
					if tools.support.battery():
						tools.battery.Battery.reset_brownout()

				# Periodic garbage to avoid memory fragmentation
				gc.collect()
				if tools.filesystem.ismicropython():
					# pylint:disable=no-member
					gc.threshold(gc.mem_free() // 5 + gc.mem_alloc())

			# Check if any problems have occurred and if a reboot is needed
			if polling_id % (3600/STEP) == 0:
				if tools.info.get_issues_counter() > 15:
					tools.system.reboot("Reboot required, %d problems detected"%tools.info.get_issues_counter())

			# Reset watch dog
			tools.watchdog.WatchDog.feed()
			await uasyncio.sleep(STEP)
			polling_id += STEP
			Periodic.current_time += STEP

	@staticmethod
	def start(**kwargs):
		""" Start periodic treatment """
		tools.logger.syslog(tools.info.sysinfo())
		tools.logger.syslog("Version: %s"%(tools.strings.tostrings(tools.builddate.date)))
		tools.logger.syslog("Config : %s"%kwargs)
		tools.tasking.Tasks.create_monitor(Periodic.task)
