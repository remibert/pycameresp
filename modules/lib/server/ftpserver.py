# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# historically based on :
# https://github.com/robert-hh/FTP-Server-for-ESP8266-ESP32-and-PYBD/blob/master/ftp.py
# but I have modified a lot, there must still be some original functions.
# pylint:disable=consider-using-f-string
""" Ftp server main class.
This class contains few lines of code, this is to save memory.
The core of the server is in the other class FtpServerCore, which is loaded into memory only when connecting an FTP client.
It takes a little while the first time you connect, but limits memory consumption if not in use.
If you have enough memory (SPIRAM or other), just start the server with the preload option at True.
"""
import server.server
import tools.logger
import tools.tasking

class FtpServerInstance(tools.tasking.ServerInstance):
	""" Ftp server instance """
	def __init__(self, **kwargs):
		tools.tasking.ServerInstance.__init__(self, **kwargs)
		self.server_class = None
		self.port = kwargs.get("ftp_port",21)

	def preload(self):
		""" Preload of ftp core class (the core is only loaded if the ftp connection started, save memory) """
		if self.server_class is None:
			tools.logger.syslog("Ftp load server")
			from server.ftpservercore import FtpServerCore
			self.server_class = FtpServerCore
			tools.logger.syslog("Ftp ready on %d"%self.port)

	async def on_connection(self, reader, writer):
		""" Asynchronous connection detected """
		try:
			# Preload ftp core class
			self.preload()

			# Start ftp core
			srv = self.server_class()

			# Call on connection method
			await srv.on_connection(reader, writer)

			# Close ftp core
			srv.close()
			del srv
		except Exception as err:
			tools.logger.syslog(err)

class FtpServer:
	""" Ftp server instance """
	config = None

	@staticmethod
	def init():
		""" Initialize http server """
		if FtpServer.config is None:
			FtpServer.config = server.server.ServerConfig()
			FtpServer.config.load_create()
		else:
			FtpServer.config.refresh()

	@staticmethod
	def start(**kwargs):
		""" Start the ftp server with asyncio loop.
		ftp_port : tcp/ip ftp port of the server default 21  """
		FtpServer.init()
		if FtpServer.config.ftp:
			kwargs["port"] = kwargs.get("ftp_port",21)
			kwargs["name"] = "Ftp"
			tools.tasking.Tasks.create_server(FtpServerInstance(**kwargs))
		else:
			tools.logger.syslog("Ftp server disabled in config")
