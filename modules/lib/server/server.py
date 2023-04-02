# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Manage server class """
from tools import jsonconfig, filesystem

class ServerConfig(jsonconfig.JsonConfig):
	""" Servers configuration """
	def __init__(self):
		jsonconfig.JsonConfig.__init__(self)
		self.ntp = True
		self.ftp = True
		self.http = True
		self.telnet = True
		self.wanip = True
		self.notify = True
		if filesystem.ismicropython():
			self.server_postponed = 7
		else:
			self.server_postponed = 1
