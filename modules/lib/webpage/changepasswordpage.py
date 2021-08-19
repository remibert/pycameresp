# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to change the user and password """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage.mainpage import *

@HttpServer.addRoute(b'/changepassword', title=b"Password", index=14)
async def changePassword(request, response, args):
	""" Function define the web page to change the user and password """
	page = mainFrame(request, response, args, b"Change password", PasswordPage.change(request, response))
	await response.sendPage(page)

