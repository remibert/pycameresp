# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to manage board """
from server.httpserver import HttpServer
from server.server     import Server
from wifi.station      import Station
from htmltemplate      import *
from webpage.mainpage  import mainFrame
from tools             import useful,lang

@HttpServer.addRoute(b'/system', title=lang.system, index=1000)
async def systemPage(request, response, args):
	""" Function define the web page to manage system of the board """
	page = mainFrame(request, response, args, lang.system_management_s%Station.getHostname(),
		Label(text=lang.configuration ),Br(),
		ImportFile(text=lang.import_, path=b"/system/importConfig", alert=lang.configuration_imported, accept=b".cfg"),
		ExportFile(text=lang.export, path=b"/system/exportConfig", filename=b"Config_%s.cfg"%Station.getHostname()),

		Br(),Br(),Label(text=lang.file_system),Br(),
		ImportFile(text=lang.import_, path=b"/system/importFileSystem", alert=lang.import_in_progress, accept=b".cfs"),
		ExportFile(text=lang.export, path=b"/system/exportFileSystem", filename=b"FileSystem_%s.cfs"%Station.getHostname()),

		Br(),Br(),Label(text=lang.syslog),Br(),
		ExportFile(text=lang.export, path=b"/system/exportSyslog", filename=b"Syslog_%s.log"%Station.getHostname()),

		Br(), Br(),Label(text=lang.reboot_device),Br(),
		ButtonCmd(text=lang.reboot,path=b"/system/reboot",confirm=b"Confirm reboot", name=b"reboot"))
	await response.sendPage(page)

@HttpServer.addRoute(b'/system/importConfig')
async def importConfig(request, response, args):
	""" Import configuration """
	Server.slowDown()
	useful.importFiles(request.getContentFilename())
	await response.sendOk()

@HttpServer.addRoute(b'/system/exportConfig')
async def exportConfig(request, response, args):
	""" Export all configuration """
	Server.slowDown()
	useful.exportFiles("config.cfg", path="./config",pattern="*.json", recursive=False)
	await response.sendFile(b"config.cfg", headers=request.headers)
	useful.remove("config.cfg")

@HttpServer.addRoute(b'/system/importFileSystem')
async def importFileSystem(request, response, args):
	""" Import file system """
	Server.slowDown()
	useful.importFiles(request.getContentFilename())
	await reboot(request, response, args)

@HttpServer.addRoute(b'/system/exportFileSystem')
async def exportFileSystem(request, response, args):
	""" Export file system """
	Server.slowDown()
	useful.exportFiles("fileSystem.cfs", path="./",pattern="*.*", recursive=True)
	await response.sendFile(b"fileSystem.cfs", headers=request.headers)
	useful.remove("fileSystem.cfs")

@HttpServer.addRoute(b'/system/exportSyslog')
async def exportSyslog(request, response, args):
	""" Export file system """
	Server.slowDown()
	await response.sendFile([b"syslog.log.4",b"syslog.log.3",b"syslog.log.2",b"syslog.log.1",b"syslog.log"], headers=request.headers)

@HttpServer.addRoute(b'/system/reboot')
async def reboot(request, response, args):
	""" Reboot device """
	try:
		await response.sendOk()
	except Exception as err:
		useful.syslog(err)
	try:
		useful.reboot("Reboot asked on system html page")
	except Exception as err:
		useful.syslog(err)
