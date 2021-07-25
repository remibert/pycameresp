# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the main web page with menu, it check also the login password """
from htmltemplate import *
from webpage.passwordpage import PasswordPage
from server.httpserver import HttpServer
from wifi.station import Station

styleNav = b"""  height: 100%;
  width: 140px;
  position: fixed;
  z-index: 1;
  top: 0;
  left: 0;
  overflow-x: hidden;
  background-color: #F4F4F4;
  padding-left:2px;
  padding-right:2px;
  padding-top:2px;
"""
styleContent = b""" 
  margin-left: 150px;
"""
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
		menus = HttpServer.getMenus()
		tabs = []
		for menu in menus:
			index, href, title_ = menu
			tabs.append(TabItem(text=title_ , href=href, active=(active==index)))
		page = Page([stylesheet, \
					Div(Tab(tabs), style=styleNav),\
					Div(content,   style=styleContent)\
					], title=title)
	else:
		page = Page(page + [stylesheet], title=b"Login")
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
		submit = Submit(text=b"Modify", name=b"action", value=b"modify")
	else:
		submit = Submit(text=b"Save", name=b"action", value=b"save", onclick=onclick)
	return disabled, action, submit