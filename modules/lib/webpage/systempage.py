# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to manage board """
from server.httpserver import HttpServer
from server.server     import Server
from wifi.station      import Station
from htmltemplate      import *
from webpage.mainpage  import main_frame
from tools             import lang,archiver,filesystem,logger,system

@HttpServer.add_route(b'/system', menu=lang.menu_system, item=lang.item_system)
async def system_page(request, response, args):
	""" Function define the web page to manage system of the board """
	page = main_frame(request, response, args, lang.system_management_s%Station.get_hostname(),
		Label(text=lang.configuration ),Br(),
		UploadFile(text=lang.upload, path=b"/system/upload_config", alert=lang.configuration_uploaded, accept=b".cfg"),
		DownloadFile(text=lang.download, path=b"/system/download_config", filename=b"Config_%s.cfg"%Station.get_hostname()),

		Br(),Br(),Label(text=lang.file_system),Br(),
		UploadFile(text=lang.upload, path=b"/system/upload_file_system", alert=lang.upload_in_progress, accept=b".cfs"),
		DownloadFile(text=lang.download, path=b"/system/download_file_system", filename=b"FileSystem_%s.cfs"%Station.get_hostname()),

		Br(),Br(),Label(text=lang.syslog),Br(),
		DownloadFile(text=lang.download, path=b"/system/download_syslog", filename=b"Syslog_%s.log"%Station.get_hostname()),

		Br(), Br(),Label(text=lang.reboot_device),Br(),
		ButtonCmd(text=lang.reboot,path=b"/system/reboot",confirm=lang.confirm_reboot, name=b"reboot"))
	await response.send_page(page)

@HttpServer.add_route(b'/system/upload_config')
async def upload_config(request, response, args):
	""" Upload configuration """
	Server.slow_down()
	file = request.get_content_filename()
	archiver.upload_files(file)
	await response.send_ok()

@HttpServer.add_route(b'/system/download_config')
async def download_config(request, response, args):
	""" Download configuration """
	Server.slow_down()
	archiver.download_files("config.cfg", path="./config",pattern="*.json", recursive=False)
	await response.send_file(b"config.cfg", headers=request.headers)
	filesystem.remove("config.cfg")

@HttpServer.add_route(b'/system/upload_file_system')
async def upload_file_system(request, response, args):
	""" Upload file system """
	Server.slow_down()
	archiver.upload_files(request.get_content_filename())
	await reboot(request, response, args)

@HttpServer.add_route(b'/system/download_file_system')
async def download_file_system(request, response, args):
	""" Download file system """
	Server.slow_down()
	archiver.download_files("fileSystem.cfs", path="./",pattern="*.*", recursive=True)
	await response.send_file(b"fileSystem.cfs", headers=request.headers)
	filesystem.remove("fileSystem.cfs")

@HttpServer.add_route(b'/system/download_syslog')
async def download_syslog(request, response, args):
	""" Download syslog """
	Server.slow_down()
	await response.send_file([b"syslog.log.4",b"syslog.log.3",b"syslog.log.2",b"syslog.log.1",b"syslog.log"], headers=request.headers)

@HttpServer.add_route(b'/system/reboot')
async def reboot(request, response, args):
	""" Reboot device """
	try:
		await response.send_ok()
	except Exception as err:
		logger.syslog(err)
	try:
		system.reboot("Reboot asked on system html page")
	except Exception as err:
		logger.syslog(err)
