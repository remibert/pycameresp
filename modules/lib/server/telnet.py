# Based on https://github.com/cpopp/MicroTelnetServer/blob/master/utelnet/utelnetserver.py
# Add user login
# pylint:disable=consider-using-f-string
# pylint:disable=consider-using-enumerate
""" Telnet class """
import socket
import sys
import uos
from server import server
from tools import logger, support, tasking

class TelnetServerInstance(tasking.ServerInstance):
	""" Telnet server instance """
	def __init__(self, **kwargs):
		tasking.ServerInstance.__init__(self, **kwargs)

	def start_server(self):
		""" Start server """
		port = self.kwargs.get("telnet_port",23)
		if support.telnet():
			# start listening for telnet connections on port 23
			try:
				Telnet.stop()
				Telnet.server[0] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				Telnet.server[0].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				ai = socket.getaddrinfo("0.0.0.0", port)
				addr = ai[0][4]
				Telnet.server[0].bind(addr)
				Telnet.server[0].listen(1)
				Telnet.server[0].setsockopt(socket.SOL_SOCKET, 20, Telnet.accept)
			except Exception as err:
				logger.syslog("Telnet unavailable '%s'"%str(err))
		return "Telnet", port

class Telnet:
	""" Telnet class connection """
	client = [None]
	server = [None]

	@staticmethod
	def accept(socket_server):
		""" Accept telnet connection """
		# Attach new clients to dupterm and
		# send telnet control characters to disable line mode
		# and stop local echoing
		Telnet.close_client()
		from server import telnetcore
		Telnet.client[0], remote_addr = socket_server.accept()
		logger.syslog("Telnet connected from : %s" % remote_addr[0])
		Telnet.client[0].setblocking(False)
		Telnet.client[0].setsockopt(socket.SOL_SOCKET, 20, uos.dupterm_notify)
		Telnet.client[0].sendall(bytes([255, 252, 34])) # dont allow line mode
		Telnet.client[0].sendall(bytes([255, 251, 1])) # turn off local echo
		uos.dupterm(telnetcore.TelnetWrapper(Telnet.client[0]))

	@staticmethod
	def close_client():
		""" Close the opened client """
		if Telnet.client[0]:
			# close any previous clients
			uos.dupterm(None)
			Telnet.client[0].close()
			Telnet.client[0] = None
			try:
				del sys.modules["server.telnetcore"]
			except:
				pass

	@staticmethod
	def stop():
		""" Stop telnet server """
		# pylint:disable=global-variable-not-assigned
		uos.dupterm(None)
		if Telnet.server[0]:
			Telnet.server[0].close()
			Telnet.server[0] = None
		Telnet.close_client()

	@staticmethod
	def start(**kwargs):
		""" Start telnet server """
		config = server.ServerConfig()
		config.load_create()
		# If telnet activated
		if config.telnet:
			tasking.Tasks.create_server(TelnetServerInstance(**kwargs))
