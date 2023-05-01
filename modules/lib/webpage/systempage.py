# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Function define the web page to manage board """
import server.httpserver
import wifi.station
from htmltemplate      import *
import webpage.mainpage
import tools.lang
import tools.archiver
import tools.filesystem
import tools.logger
import tools.system
import tools.tasking

@server.httpserver.HttpServer.add_route(b'/system', menu=tools.lang.menu_system, item=tools.lang.item_system)
async def system_page(request, response, args):
	""" Function define the web page to manage system of the board """
	page = webpage.mainpage.main_frame(request, response, args, tools.lang.system_management_s%wifi.station.Station.get_hostname(),
		Form([
			FormGroup([
				Label(text=tools.lang.configuration ), Br(),
				UploadFile  (text=tools.lang.upload,   path=b"/system/upload_config",   alert=tools.lang.configuration_uploaded, accept=b".cfs"), Space(),
				DownloadFile(text=tools.lang.download, path=b"/system/download_config", filename=b"%s.config.cfs"%wifi.station.Station.get_hostname()),
			]),
			FormGroup([
				Label(text=tools.lang.file_system), Br(),
				UploadFile  (text=tools.lang.upload,   path=b"/system/upload_file_system",   alert=tools.lang.upload_in_progress, accept=b".cfs"), Space(),
				DownloadFile(text=tools.lang.download, path=b"/system/download_file_system", filename=b"%s.filesystem.cfs"%wifi.station.Station.get_hostname()),
			]),
			FormGroup([
				Label(text=tools.lang.syslog), Br(),
				DownloadFile(text=tools.lang.download, path=b"/system/download_syslog", filename=b"%s.syslog.log"%wifi.station.Station.get_hostname()),
			]),
			FormGroup([
				Label(text=tools.lang.reboot_device), Br(),
				ButtonCmd(text=tools.lang.reboot,path=b"/system/reboot",confirm=tools.lang.confirm_reboot, name=b"reboot")
			])
		])
	)
	await response.send_page(page)

@server.httpserver.HttpServer.add_route(b'/system/upload_config')
async def upload_config(request, response, args):
	""" Upload configuration """
	tools.tasking.Tasks.slow_down()
	file = request.get_content_filename()
	tools.archiver.upload_files(file)
	await response.send_ok()

@server.httpserver.HttpServer.add_route(b'/system/download_config')
async def download_config(request, response, args):
	""" Download configuration """
	tools.tasking.Tasks.slow_down()
	tools.archiver.download_files("config.cfg", path="./config", pattern="*.json", excludes=["*.tmp","sd/*",".DS_Store"], recursive=False)
	await response.send_file(b"config.cfg", headers=request.headers)
	tools.filesystem.remove("config.cfg")

@server.httpserver.HttpServer.add_route(b'/system/upload_file_system')
async def upload_file_system(request, response, args):
	""" Upload file system """
	tools.tasking.Tasks.slow_down()
	tools.archiver.upload_files(request.get_content_filename())
	await reboot(request, response, args)

@server.httpserver.HttpServer.add_route(b'/system/download_file_system')
async def download_file_system(request, response, args):
	""" Download file system """
	tools.tasking.Tasks.slow_down()
	tools.archiver.download_files("fileSystem.cfs", path="./",pattern="*.*", excludes=["*.tmp","config/*","sd/*","syslog.*","www/bootstrap.*",".DS_Store"], recursive=True)
	await response.send_file(b"fileSystem.cfs", headers=request.headers)
	tools.filesystem.remove("fileSystem.cfs")

@server.httpserver.HttpServer.add_route(b'/system/download_syslog')
async def download_syslog(request, response, args):
	""" Download syslog """
	tools.tasking.Tasks.slow_down()
	await response.send_file([b"syslog.log.4",b"syslog.log.3",b"syslog.log.2",b"syslog.log.1",b"syslog.log"], headers=request.headers)

@server.httpserver.HttpServer.add_route(b'/system/reboot')
async def reboot(request, response, args):
	""" Reboot device """
	try:
		await response.send_ok()
	except Exception as err:
		tools.logger.syslog(err)
	try:
		tools.system.reboot("Reboot asked on system html page")
	except Exception as err:
		tools.logger.syslog(err)
