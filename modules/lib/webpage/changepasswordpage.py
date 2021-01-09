# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to change the user and password """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage import *

@HttpServer.addRoute('/changepassword', title=b"Password", index=14)
async def changePassword(request, response, args):
	""" Function define the web page to change the user and password """
	page = mainPage(content=[PasswordPage.change(request, response)], title=b"Change password", active=args["index"], request=request, response=response)
	await response.sendPage(page)
