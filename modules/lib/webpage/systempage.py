# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to manage board """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage import *
from tools import useful
from tools.useful import log
import sys
import gc

@HttpServer.addRoute(b'/system', title=b"System", index=20)
async def systemPage(request, response, args):
	""" Function define the web page to manage system of the board """
	page = mainFrame(request, response, args, b"System management",
		Label(text=b"Configuration"),Br(),
		ImportFile(text=b"Import", path=b"/system/importConfig", alert=b"Configuration imported", accept=b".cfg"),
		ExportFile(text=b"Export", path=b"/system/exportConfig", filename=b"Config.cfg"),

		Br(),Br(),Label(text=b"File system"),Br(),
		ImportFile(text=b"Import", path=b"/system/importFileSystem", alert=b"Import in progress, wait a few minutes the automatic reboot", accept=b".cfs"),
		ExportFile(text=b"Export", path=b"/system/exportFileSystem", filename=b"FileSystem.cfs"),

		Br(), Br(),Label(text=b"Reboot device"),Br(),
		ButtonCmd(text=b"Reboot",path=b"/system/reboot",confirm=b"Confirm reboot", name=b"reboot"))
	await response.sendPage(page)

@HttpServer.addRoute(b'/system/importConfig')
async def importConfig(request, response, args):
	""" Import configuration """
	useful.importFiles(request.getContentFilename())
	await response.sendOk()

@HttpServer.addRoute(b'/system/exportConfig')
async def exportConfig(request, response, args):
	""" Export all configuration """
	useful.exportFiles("config.cfg", path="./config",pattern="*.json", recursive=False)
	await response.sendFile(b"config.cfg", headers=request.headers)
	useful.remove("config.cfg")

@HttpServer.addRoute(b'/system/importFileSystem')
async def importFileSystem(request, response, args):
	""" Import file system """
	useful.importFiles(request.getContentFilename())
	await reboot(request, response, args)

@HttpServer.addRoute(b'/system/exportFileSystem')
async def exportFileSystem(request, response, args):
	""" Export file system """
	useful.exportFiles("fileSystem.cfs", path="./",pattern="*.*", recursive=True)
	await response.sendFile(b"fileSystem.cfs", headers=request.headers)
	useful.remove("fileSystem.cfs")

@HttpServer.addRoute(b'/system/reboot')
async def reboot(request, response, args):
	""" Reboot device """
	try:
		await response.sendOk()
	except Exception as err:
		print(useful.exception(err))
	try:
		import machine
		print("Reboot")
		machine.reset()
	except Exception as err:
		print(useful.exception(err))
