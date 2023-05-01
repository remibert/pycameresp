# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Function define the main web page with menu, it check also the login password """
from htmltemplate import *
import webpage.passwordpage
import server.httpserver
import wifi.station
import tools.lang
import tools.tasking

def main_page(request, response, args, title_frame, content=None, menu_visible=True):
	""" Function define the main web page with menu, it check also the login password """
	try:
		title  = args["title"]
	except:
		title = title_frame
	try:
		active = args["index"]
	except:
		active = 0
	# On wifi station, the external style cheet is added
	if wifi.station.Station.is_ip_on_interface(request.remoteaddr):
		stylesheet = Stylesheet()
	else:
		stylesheet = StylesheetDefault()

	# Create main page if logged
	page = webpage.passwordpage.PasswordPage.login(request, response, 15*60)

	if b"logout" in request.params and page is None:
		content = None

	if page is None:
		if menu_visible:
			menu_items = []
			menu_bar = []
			previous_menu = None
			for menu,  item , index, href in server.httpserver.HttpServer.get_menus():
				menu_item = MenuItem(text=item, href=href, active=(active==index))

				if previous_menu != menu:
					if previous_menu is not None:
						menu_bar.append(Menu(menu_items, text=previous_menu))
					menu_items = [menu_item]
					previous_menu = menu
				else:
					menu_items.append(menu_item)
			menu_bar.append(Menu(menu_items, text=previous_menu))
			page_content = [stylesheet, MenuBar(menu_bar), Div(content)]
		else:
			page_content = [stylesheet, content]
		page = Page(page_content, class_=b"container", title=title, style=b"padding-top: 4.5rem;")
	else:
		page = Page([page] + [stylesheet], title=tools.lang.login)
	tools.tasking.Tasks.slow_down()
	return page

def main_frame(request, response, args, title_frame, *content):
	""" Function define the main frame into the main page with menu, it check also the login password """
	internal = [Title3(text=title_frame, style=b"padding-top:0.5em;padding-bottom:0.5em;"),content, Br(), Br(),Br()]
	return main_page(request, response, args, title_frame, content=internal)

def manage_default_button(request, config, callback=None, onclick=b""):
	""" Manage the 'modify' and 'save' button on the page """
	if config.load() is False:
		config.save()
	action = request.params.get(b"action",b"none")
	disabled = False
	if   action == b"none":
		disabled = True
	elif action == b"modify":
		disabled = False
	elif action == b"save":
		disabled = True
		config.update(request.params, show_error=False)
		if callback:
			callback(request, config)
		config.save()
	if disabled:
		submit = Submit(text=tools.lang.modify, name=b"action", value=b"modify")
	else:
		submit = Submit(text=tools.lang.save, name=b"action", value=b"save", onclick=onclick)
	return disabled, action, submit
