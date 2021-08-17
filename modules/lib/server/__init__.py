# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class for servers FTP, HTTP, Telnet.
Class to dialog with NTP, PushOver. 
Class to manage session, user password, stream."""

def init(loop=None, pageLoader=None, preload=False, httpPort=80):
	""" Init servers
	loop : asyncio loop
	pageLoader : callback to load html page
	preload : True force the load of page at the start, 
	False the load of page is done a the first http connection (Takes time on first connection) """
	from server.server import Server
	Server.init(loop, pageLoader, preload, httpPort)
