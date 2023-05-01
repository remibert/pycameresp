# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Manage server class """
import tools.jsonconfig
import tools.filesystem

class ServerConfig(tools.jsonconfig.JsonConfig):
	""" Servers configuration """
	def __init__(self):
		tools.jsonconfig.JsonConfig.__init__(self)
		self.ntp = True
		self.ftp = True
		self.http = True
		self.telnet = True
		self.wanip = True
		self.notify = True
		if tools.filesystem.ismicropython():
			self.server_postponed = 7
		else:
			self.server_postponed = 1
