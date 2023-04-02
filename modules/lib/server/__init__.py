# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class for servers FTP, HTTP, Telnet.
Class to dialog with NTP, PushOver.
Class to manage session, user password, stream."""

def init(loop=None, **kwargs):
	""" Init servers
	loop : asyncio loop
	http_port : port of http server """
	from server.server import Server
	Server.init(loop, **kwargs)
