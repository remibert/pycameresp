# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to change the user and password """
from server.httpserver import HttpServer
from server.user       import User
from htmltemplate      import *
from webpage.mainpage  import *
from tools             import lang

@HttpServer.add_route(b'/changepassword', menu=lang.menu_account, item=lang.item_password)
async def change_password(request, response, args):
	""" Function define the web page to change the user and password """
	page = main_frame(request, response, args, lang.change_password, PasswordPage.change(request, response))
	await response.send_page(page)

@HttpServer.add_route(b'/logout', menu=lang.menu_account, item=lang.item_logout)
async def logout(request, response, args):
	""" Function to close account """
	if not User.is_empty():
		page = main_frame(request, response, args, lang.logout, PasswordPage.logout(request,response))
	else:
		page = main_frame(request, response, args, lang.logout, None)
	await response.send_page(page)
