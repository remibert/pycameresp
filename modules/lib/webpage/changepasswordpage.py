# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Function define the web page to change the user and password """
import server.httpserver
import server.user
from htmltemplate      import *
import webpage.mainpage
import webpage.passwordpage
import tools.lang

@server.httpserver.HttpServer.add_route(b'/changepassword', menu=tools.lang.menu_account, item=tools.lang.item_password)
async def change_password(request, response, args):
	""" Function define the web page to change the user and password """
	page = webpage.mainpage.main_frame(request, response, args, tools.lang.change_password, webpage.passwordpage.PasswordPage.change(request, response))
	await response.send_page(page)

@server.httpserver.HttpServer.add_route(b'/logout', menu=tools.lang.menu_account, item=tools.lang.item_logout)
async def logout(request, response, args):
	""" Function to close account """
	if not server.user.User.is_empty():
		request.params[b"logout"] = b"1"
		webpage.passwordpage.PasswordPage.logout(request,response)
	page = webpage.mainpage.main_frame(request, response, args, tools.lang.logout)
	await response.send_page(page)
