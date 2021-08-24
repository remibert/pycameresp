# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to change the user and password """
from server.httpserver import HttpServer
from htmltemplate      import *
from webpage.mainpage  import *
from tools             import lang


@HttpServer.addRoute(b'/changepassword', title=lang.password, index=100)
async def changePassword(request, response, args):
	""" Function define the web page to change the user and password """
	page = mainFrame(request, response, args, lang.change_password, PasswordPage.change(request, response))
	await response.sendPage(page)

