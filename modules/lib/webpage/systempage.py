# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to manage board """
from server.httpserver import HttpServer
from server.server   import Server
from wifi.station import Station
from htmltemplate import *
from webpage import *
from tools import useful
import uasyncio
import sys
import gc

@HttpServer.addRoute(b'/system', title=b"System", index=300)
async def systemPage(request, response, args):
	""" Function define the web page to manage system of the board """
	page = mainFrame(request, response, args, b"System management %s"%Station.getHostname(),
		Label(text=b"Configuration" ),Br(),
		ImportFile(text=b"Import", path=b"/system/importConfig", alert=b"Configuration imported", accept=b".cfg"),
		ExportFile(text=b"Export", path=b"/system/exportConfig", filename=b"Config_%s.cfg"%Station.getHostname()),

		Br(),Br(),Label(text=b"File system"),Br(),
		ImportFile(text=b"Import", path=b"/system/importFileSystem", alert=b"Import in progress, wait a few minutes the automatic reboot", accept=b".cfs"),
		ExportFile(text=b"Export", path=b"/system/exportFileSystem", filename=b"FileSystem_%s.cfs"%Station.getHostname()),

		Br(),Br(),Label(text=b"Trace"),Br(),
		ExportFile(text=b"Trace", path=b"/system/exportTrace", filename=b"trace_%s.log"%Station.getHostname()),

		Br(), Br(),Label(text=b"Reboot device"),Br(),
		ButtonCmd(text=b"Reboot",path=b"/system/reboot",confirm=b"Confirm reboot", name=b"reboot"))
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

@HttpServer.addRoute(b'/system/exportTrace')
async def exportTrace(request, response, args):
	""" Export file system """
	Server.slowDown()
	await response.sendFile([b"trace.log.4",b"trace.log.3",b"trace.log.2",b"trace.log.1",b"trace.log"], headers=request.headers)

@HttpServer.addRoute(b'/system/reboot')
async def reboot(request, response, args):
	""" Reboot device """
	try:
		await response.sendOk()
	except Exception as err:
		useful.exception(err)
	try:
		useful.reboot("Reboot asked on system html page")
	except Exception as err:
		useful.exception(err)
