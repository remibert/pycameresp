# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the main web page with menu, it check also the login password """
from htmltemplate import *
from webpage.passwordpage import PasswordPage
from server.httpserver import HttpServer
from server.server   import Server
from wifi.station import Station
from tools import lang

def mainPage(request, response, args, content=None):
	""" Function define the main web page with menu, it check also the login password """

	try:
		title  = args["title"]
	except:
		title = b""
	try:
		active = args["index"]
	except:
		active = 0

	# On wifi station, the external style cheet is added
	if Station.isIpOnInterface(request.remoteaddr):
		# stylesheet = StylesheetDefault()
		stylesheet = Stylesheet()
	else:
		stylesheet = StylesheetDefault()

	# Create main page if logged
	page = PasswordPage.login(request, response, 15*60)

	if page == None:
		menuItems = []
		menus = []
		menuBar = []
		previousMenu = None
		for menu,  item , index, href in HttpServer.getMenus():
			menuItem = MenuItem(text=item, href=href, active=(active==index))

			if previousMenu != menu:
				if previousMenu is not None:
					menuBar.append(Menu(menuItems, text=previousMenu))
				menuItems = [menuItem]
				previousMenu = menu
			else:
				menuItems.append(menuItem)
		menuBar.append(Menu(menuItems, text=previousMenu))
		page = Page([stylesheet, MenuBar(menuBar), content], title=title)
	else:
		page = Page(page + [stylesheet], title=lang.login)
	Server.slowDown()
	return page

def mainFrame(request, response, args, titleFrame, *content):
	""" Function define the main frame into the main page with menu, it check also the login password """
	internal = [Container([Card([Form([Title3(text=titleFrame, style=b"padding-top:0.5em;padding-bottom:0.5em;"),content,])], class_=b"shadow")], style=b"margin-top:1em")]
	return mainPage(request, response, args, content=internal)

def manageDefaultButton(request, config, callback=None, onclick=b""):
	""" Manage the 'modify' and 'save' button on the page """
	if config.load() == False:
		config.save()
	action = request.params.get(b"action",b"none")
	disabled = False
	if   action == b"none":
		disabled = True
	elif action == b"modify":
		disabled = False 
	elif action == b"save":
		disabled = True
		config.update(request.params)
		if callback:
			callback(request, config)
		config.save()
	if disabled:
		submit = Submit(text=lang.modify, name=b"action", value=b"modify")
	else:
		submit = Submit(text=lang.save, name=b"action", value=b"save", onclick=onclick)
	return disabled, action, submit