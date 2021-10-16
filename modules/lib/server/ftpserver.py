# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# historically based on :
# https://github.com/robert-hh/FTP-Server-for-ESP8266-ESP32-and-PYBD/blob/master/ftp.py
# but I have modified a lot, there must still be some original functions.
""" Ftp server main class.
This class contains few lines of code, this is to save memory.
The core of the server is in the other class FtpServerCore, which is loaded into memory only when connecting an FTP client.
It takes a little while the first time you connect, but limits memory consumption if not in use.
If you have enough memory (SPIRAM or other), just start the server with the preload option at True.
"""
import uasyncio
from tools import useful

class Ftp:
	""" Ftp main class """
	def __init__(self, port=21, preload=False):
		self.server_class = None
		self.port = port
		if preload:
			self.preload()
		else:
			useful.syslog("Ftp waiting on %d"%self.port)

	def preload(self):
		""" Preload of ftp core class (the core is only loaded if the ftp connection started, save memory) """
		if self.server_class is None:
			useful.syslog("Ftp load server")
			from server.ftpservercore import FtpServerCore
			self.server_class = FtpServerCore
			useful.syslog("Ftp ready on %d"%self.port)

	async def on_connection(self, reader, writer):
		""" Asynchronous connection detected """
		try:
			# Preload ftp core class
			self.preload()

			# Start ftp core
			server = self.server_class()

			# Call on connection method
			await server.on_connection(reader, writer)

			# Close ftp core
			server.close()
			del server
		except Exception as err:
			useful.syslog(err)

def start(loop=None, port=21, preload=False):
	""" Start the ftp server with asyncio loop.
	loop : asyncio loop object
	port : tcp/ip port of the server
	preload : True = preload the server at the start, False = load the server at the first connection """
	server = Ftp(port, preload)

	# If asyncio loop not created
	if loop is None:
		# Create asyncio loop
		loop = uasyncio.get_event_loop()

		# Run for ever in this case the ftp server
		run_forever = True
	else:
		# The ftp server is called on asyncio connection
		run_forever = False

	# Start ftp server on port specified
	asyncServer = uasyncio.start_server(server.on_connection, "0.0.0.0", port, backlog=1)

	# Create asyncio task
	loop.create_task(asyncServer)

	# If ftp server is stand alone mode
	if run_forever:
		loop.run_forever()

if __name__ == "__main__":
	start()
