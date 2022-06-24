# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Periodic task, wifi management, get wan_ip, synchronize time """
import uasyncio
from server.server import ServerConfig, Server
import wifi
from tools import battery, lang, awake, tasking, watchdog, info, system

async def periodic_task():
	""" Periodic task """
	periodic = Periodic()
	await tasking.task_monitoring(periodic.task)

class Periodic:
	""" Class to manage periodic task """
	def __init__(self):
		""" Constructor """
		self.server_config = ServerConfig()
		self.server_config.load()
		self.get_login_state = None
		watchdog.WatchDog.start(watchdog.SHORT_WATCH_DOG)

	async def check_login(self):
		""" Inform that login detected """
		# Login state not yet get
		if self.get_login_state is None:
			from server.user import User
			self.get_login_state = User.get_login_state

		# Get login state
		login =  self.get_login_state()

		# If login detected
		if login is not None:
			from server.notifier import Notifier
			if login:
				await Notifier.notify(lang.login_success_detected, display=False, enabled=self.server_config.notify)
			else:
				await Notifier.notify(lang.login_failed_detected,  display=False, enabled=self.server_config.notify)

	async def task(self):
		""" Periodic task method """
		polling_id = 0

		watchdog.WatchDog.start(watchdog.SHORT_WATCH_DOG)
		while True:
			# Reload server config if changed
			if polling_id % 5 == 0:
				# Manage login user
				await self.check_login()

				if self.server_config.is_changed():
					self.server_config.load()

			# Manage server
			await Server.manage(polling_id)

			# Manage awake duration
			awake.Awake.manage()

			# Reset brownout counter if wifi connected
			if wifi.Wifi.is_wan_connected():
				battery.Battery.reset_brownout()

			# Reset watch dog
			watchdog.WatchDog.feed()
			await uasyncio.sleep(1)
			polling_id += 1

			# Check if any problems have occurred and if a reboot is needed
			if polling_id % 3607:
				if info.get_issues_counter() > 15:
					system.reboot("Reboot required, %d problems detected"%info.get_issues_counter())
