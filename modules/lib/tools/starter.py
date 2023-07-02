# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Allows automatic plugin start without editing python scripts.
This searches for __startup__.py files in lib directory and runs the 'startup' function """
import tools.logger
import tools.filesystem
import tools.tasking

starter_kwargs = None
class Starter:
	""" Automatic plugin start without editing python script """
	@staticmethod
	async def task(**kwargs):
		""" Starter of plugins """
		global starter_kwargs
		directories,filenames = await tools.filesystem.ascandir("lib/plugins","__startup__.py",True)
		for startup in filenames:
			startup = startup.replace("lib/","")
			startup = startup.replace(".py","")
			startup = startup.replace("/",".")

			try:
				# pylint:disable=consider-using-f-string
				exec("import %s"%startup)
				starter_kwargs = kwargs
				exec("%s.startup(**starter_kwargs)"%startup)
				starter_kwargs = None
				tools.logger.syslog("Start %s"%startup[:-12])
			except Exception as err:
				tools.logger.syslog(err)

	@staticmethod
	def start(**kwargs):
		""" Start plugin starter """
		tools.tasking.Tasks.create_task(Starter.task(**kwargs))
