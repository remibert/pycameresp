# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to manage board """
from server.httpserver import HttpServer
from server.server     import Server
from wifi.station      import Station
from htmltemplate      import *
from webpage.mainpage  import main_frame
from tools             import useful,lang,archiver

@HttpServer.add_route(b'/system', menu=lang.menu_system, item=lang.item_system)
async def system_page(request, response, args):
	""" Function define the web page to manage system of the board """
	page = main_frame(request, response, args, lang.system_management_s%Station.get_hostname(),
		Label(text=lang.configuration ),Br(),
		ImportFile(text=lang.import_, path=b"/system/import_config", alert=lang.configuration_imported, accept=b".cfg"),
		ExportFile(text=lang.export, path=b"/system/export_config", filename=b"Config_%s.cfg"%Station.get_hostname()),

		Br(),Br(),Label(text=lang.file_system),Br(),
		ImportFile(text=lang.import_, path=b"/system/import_file_system", alert=lang.import_in_progress, accept=b".cfs"),
		ExportFile(text=lang.export, path=b"/system/export_file_system", filename=b"FileSystem_%s.cfs"%Station.get_hostname()),

		Br(),Br(),Label(text=lang.syslog),Br(),
		ExportFile(text=lang.export, path=b"/system/export_syslog", filename=b"Syslog_%s.log"%Station.get_hostname()),

		Br(), Br(),Label(text=lang.reboot_device),Br(),
		ButtonCmd(text=lang.reboot,path=b"/system/reboot",confirm=lang.confirm_reboot, name=b"reboot"))
	await response.send_page(page)

@HttpServer.add_route(b'/system/import_config')
async def import_config(request, response, args):
	""" Import configuration """
	Server.slow_down()
	file = request.get_content_filename()
	archiver.import_files(file)
	await response.send_ok()

@HttpServer.add_route(b'/system/export_config')
async def export_config(request, response, args):
	""" Export all configuration """
	Server.slow_down()
	archiver.export_files("config.cfg", path="./config",pattern="*.json", recursive=False)
	await response.send_file(b"config.cfg", headers=request.headers)
	useful.remove("config.cfg")

@HttpServer.add_route(b'/system/import_file_system')
async def import_file_system(request, response, args):
	""" Import file system """
	Server.slow_down()
	archiver.import_files(request.get_content_filename())
	await reboot(request, response, args)

@HttpServer.add_route(b'/system/export_file_system')
async def export_file_system(request, response, args):
	""" Export file system """
	Server.slow_down()
	archiver.export_files("fileSystem.cfs", path="./",pattern="*.*", recursive=True)
	await response.send_file(b"fileSystem.cfs", headers=request.headers)
	useful.remove("fileSystem.cfs")

@HttpServer.add_route(b'/system/export_syslog')
async def export_syslog(request, response, args):
	""" Export file system """
	Server.slow_down()
	await response.send_file([b"syslog.log.4",b"syslog.log.3",b"syslog.log.2",b"syslog.log.1",b"syslog.log"], headers=request.headers)

@HttpServer.add_route(b'/system/reboot')
async def reboot(request, response, args):
	""" Reboot device """
	try:
		await response.send_ok()
	except Exception as err:
		useful.syslog(err)
	try:
		useful.reboot("Reboot asked on system html page")
	except Exception as err:
		useful.syslog(err)
