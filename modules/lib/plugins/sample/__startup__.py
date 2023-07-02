# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
# pylint:disable=unused-import
# pylint:disable=consider-using-f-string
""" Example of task starter """
import gc
import uasyncio
import server.httpserver
import tools.tasking
import tools.info
import tools.strings
import tools.filesystem

# Addition of the html page loader, the call will be made during the first connection to the server
@server.httpserver.HttpServer.add_pages()
def html_pages():
	""" Load html pages when connecting to http server """
	import plugins.sample.websample

async def task(**kwargs):
	""" Example of asynchronous task """
	# This task is protected against exceptions, if an uncaught exception occurs, this task will be automatically restarted.
	# If there are too many unhandled exceptions, the device reboots.
	# A crash trace is kept in the syslog file
	while True:
		gc.collect()
		print(tools.strings.tostrings(tools.info.meminfo()))
		if tools.filesystem.ismicropython():
			await uasyncio.sleep(10)
		else:
			await uasyncio.sleep(3600)

def startup(**kwargs):
	""" This function is called automatically by the starter.
	It must receive the asynchronous loop object as a parameter. """
	# Register the user task, monitor all exceptions
	import plugins.sample.mqttsample
	tools.tasking.Tasks.create_monitor(task)
