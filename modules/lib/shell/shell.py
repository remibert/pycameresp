# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=too-many-lines
# pylint:disable=consider-using-f-string
# pylint:disable=unspecified-encoding
""" Class defining a minimalist shell, directly executable on the board.
We modify directories, list, delete, move files, edit files ...
"""
# pylint:disable=wrong-import-position
import sys
sys.path.append("lib")
sys.path.append("simul")
from tools import logger,filesystem,terminal,watchdog,console

async def shell_task():
	""" Asynchronous shell task """
	import uasyncio
	try:
		from server.server import Server
	except:
		Server = None

	console.Console.print("\nPress key to start shell")
	if filesystem.ismicropython():
		polling1 = 2
		polling2 = 0.01
	else:
		polling1 = 0.1
		polling2 = 0.5
	while 1:
		# If key pressed
		if terminal.kbhit(polling2):
			character = terminal.getch()[0]

			# Check if character is correct to start shell
			if not ord(character) in [0,0xA]:
				# Ask to suspend server during shell
				if Server is not None:
					Server.suspend()

					# Wait all server suspended
					await Server.wait_all_suspended()

				# Extend watch dog duration
				watchdog.WatchDog.start(watchdog.LONG_WATCH_DOG*2)

				# Get the size of screen
				terminal.refresh_screen_size()

				# Start shell
				print("")
				logger.syslog("<"*10+" Enter shell " +">"*10)
				print("Use 'exit' to restart server or 'quit' to get python prompt")
				import shell.shellcore
				shell.shellcore.shell_sh(throw=True)
				print("")
				logger.syslog("<"*10+" Exit  shell " +">"*10)

				del sys.modules["shell.shellcore"]

				# Resume watch dog duration
				watchdog.WatchDog.start(watchdog.SHORT_WATCH_DOG)

				# Resume server
				if Server is not None:
					Server.resume()
		else:
			await uasyncio.sleep(polling1)
