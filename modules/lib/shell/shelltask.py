# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
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
import tools.logger
import tools.filesystem
import tools.terminal
import tools.watchdog
import tools.console
import tools.tasking

class Shell:
	""" Shell """
	@staticmethod
	def start():
		""" Start shell task """
		tools.tasking.Tasks.loop.create_task(Shell.task())

	@staticmethod
	async def task():
		""" Asynchronous shell task """
		import uasyncio

		tools.console.Console.print("\nPress key to start shell")
		if tools.filesystem.ismicropython():
			polling1 = 2
			polling2 = 0.01
		else:
			polling1 = 0.1
			polling2 = 0.5
		while 1:
			# If key pressed
			if tools.terminal.kbhit(polling2):
				character = tools.terminal.getch()[0]

				# Check if character is correct to start shell
				if not ord(character) in [0,0xA]:
					tools.tasking.Tasks.suspend()

					# Wait all server suspended
					await tools.tasking.Tasks.wait_all_suspended()

					# Extend watch dog duration
					tools.watchdog.WatchDog.start(tools.watchdog.LONG_WATCH_DOG*2)

					# Get the size of screen
					tools.terminal.refresh_screen_size()

					# Start shell
					print("")
					tools.logger.syslog("<"*10+" Enter shell " +">"*10)
					print("Use 'exit' to restart server or 'quit' to get python prompt")
					from shell.commands import commands
					commands(throw=True)
					print("")
					tools.logger.syslog("<"*10+" Exit  shell " +">"*10)

					del sys.modules["shell.commands"]

					# Resume watch dog duration
					tools.watchdog.WatchDog.start(tools.watchdog.SHORT_WATCH_DOG)

					# Resume server
					tools.tasking.Tasks.resume()
			else:
				await uasyncio.sleep(polling1)
