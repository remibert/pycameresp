# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Periodic task, wifi management, get wan_ip, synchronize time """
import uasyncio
from server.server import ServerConfig, Server
import wifi
from tools import battery, lang, awake, tasking

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
		tasking.WatchDog.start(tasking.SHORT_WATCH_DOG)

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
			# If notification must be send
			if self.server_config.notify:
				if login:
					await Notifier.notify(lang.login_success_detected, display=False)
				else:
					await Notifier.notify(lang.login_failed_detected, display=False)

	async def task(self):
		""" Periodic task method """
		polling_id = 0

		tasking.WatchDog.start(tasking.SHORT_WATCH_DOG)
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

			# Manage battery level
			battery.Battery.manage(wifi.Wifi.is_wan_connected())

			# Reset watch dog
			tasking.WatchDog.feed()
			await uasyncio.sleep(1)
			polling_id += 1
