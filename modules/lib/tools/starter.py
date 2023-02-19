# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Allows automatic component start without editing python scripts.
This searches for __startup__.py files in lib directory and runs the 'startup' function """
from tools.filesystem import ascandir
from tools.logger import syslog

async def starter_task(loop):
	""" Starter of components """
	directories,filenames = await ascandir("lib","__startup__.py",True)
	for startup in filenames:
		startup = startup.replace("lib/","")
		startup = startup.replace(".py","")
		startup = startup.replace("/",".")

		try:
			# pylint:disable=consider-using-f-string
			exec("import %s"%startup)
			exec("%s.startup(loop)"%startup)
			syslog("Start component %s"%startup[:-12])
		except Exception as err:
			syslog(err)
