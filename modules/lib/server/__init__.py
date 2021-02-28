# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class for servers FTP, HTTP, Telnet.
Class to dialog with NTP, PushOver. 
Class to manage session, user password, stream."""
from server import *
from server.sessions import *
from server.user import *
from server.pushover import *
from tools import jsonconfig
from tools import useful

class ServerConfig:
	""" Servers configuration """
	def __init__(self):
		self.ntp = True
		self.ftp = True
		self.http = True
		self.telnet = True
		self.offsettime = 1

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

def start(loop=None, pageLoader=None, preload=False, withoutServer=False):
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
			import server.timesetting
			server.timesetting.setdate(config.offsettime)

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
			server.httpserver.start(loop=loop, loader=pageLoader, preload=preload, port=8080)

			# If camera present
			if useful.iscamera():
				# Load and start streaming http server
				server.httpserver.start(loop=loop, loader=pageLoader, preload=preload, port=8081)
	
	# Display system informations
	useful.sysinfo()