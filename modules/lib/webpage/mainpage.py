# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the main web page with menu, it check also the login password """
from htmltemplate import *
from webpage.passwordpage import PasswordPage
from server.httpserver import HttpServer
from wifi.station import Station

def mainPage(title="", active=0, content=None, request=None, response=None):
	""" Function define the main web page with menu, it check also the login password """
	# On wifi station, the external style cheet is added
	if Station.isIpOnInterface(request.remoteaddr):
		stylesheet = Stylesheet()
	else:
		stylesheet = None

	# Create main page if logged
	page = PasswordPage.login(request, response, 15*60)

	if page == None:
		menus = HttpServer.getMenus()
		tabs = []
		for menu in menus:
			index, href, title_ = menu
			tabs.append(TabItem(text=title_, href=href, active=(active==index)))
		page = Page([stylesheet, Title2(text=title), Tab(tabs), content], title=title)
	else:
		page = Page(page + [stylesheet], title=b"Login")
	return page
