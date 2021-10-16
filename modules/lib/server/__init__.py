# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class for servers FTP, HTTP, Telnet.
Class to dialog with NTP, PushOver.
Class to manage session, user password, stream."""

def init(loop=None, page_loader=None, preload=False, http_port=80):
	""" Init servers
	loop : asyncio loop
	page_loader : callback to load html page
	preload : True force the load of page at the start,
	False the load of page is done a the first http connection (Takes time on first connection) """
	from server.server import Server
	Server.init(loop, page_loader, preload, http_port)
