# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class for servers FTP, HTTP, Telnet.
Class to dialog with NTP, PushOver. 
Class to manage session, user password, stream."""
from server import *
from server.sessions import *
from server.user import *
from server.pushover import *
from server.wanip import *
from server.ping import *
from server.dnsclient import *
from server.timesetting import *
from tools import jsonconfig
from tools import useful
import uasyncio


class ServerConfig:
	""" Servers configuration """
	def __init__(self):
		self.ntp = True
		self.ftp = True
		self.http = True
		self.telnet = True
		self.offsettime = 1
		self.dst = True

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

def start(loop=None, pageLoader=None, preload=False, withoutServer=False, httpPort=80):
	""" Start all servers
	loop : asyncio loop
	pageLoader : callback to load html page
	preload : True force the load of page at the start, 
	False the load of page is done a the first http connection (Takes time on first connection) """
	from tools import useful
	import wifi
	
	# If wifi started
	if wifi.start():
		from server import ServerConfig
		config = ServerConfig()
		if config.load() == False:
			config.save()

		# If ntp synchronisation activated
		if config.ntp:
			# Load and start ntp synchronisation
			loop.create_task(periodic())

		# If telnet activated
		if config.telnet and withoutServer == False:
			# Load and start telnet
			import server.telnet
			server.telnet.start()

		# If ftp activated
		if config.ftp and withoutServer == False:
			# Load and start ftp server
			import server.ftpserver
			server.ftpserver.start(loop=loop, preload=preload)

		# If http activated
		if config.http and withoutServer == False:
			# Load and start http server
			import server.httpserver
			server.httpserver.start(loop=loop, loader=pageLoader, preload=preload, port=httpPort, name="httpServer")

			# If camera present
			if useful.iscamera():
				# Load and start streaming http server
				server.httpserver.start(loop=loop, loader=pageLoader, preload=preload, port=httpPort +1, name="StreamingServer")
	
	# Display system informations
	useful.sysinfo()


async def periodic():
	""" Periodic traitment update time, get wanip """
	while True:
		config = server.ServerConfig()
		config.load()
		if config.ntp:
			setdate(config.offsettime, dst=config.dst, display=True)
		await uasyncio.sleep(3600)


_suspended = [False]
def suspend():
	""" Suspend the asyncio task of servers """
	_suspended[0] = True

def resume():
	""" Resume the asyncio task of servers """
	_suspended[0] = False

async def waitResume():
	""" Wait the resume of task servers """
	if _suspended[0]:
		while _suspended[0]:
			await uasyncio.sleep(1)
