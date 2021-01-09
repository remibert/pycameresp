# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the pushover notifications """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage import *
from server.pushover import *

@HttpServer.addRoute(b'/pushover', title=b"Pushover", index=15)
async def pushover(request, response, args):
	""" Function define the web page to configure the pushover notifications """
	config = PushOverConfig()
	config.load()

	action = request.params.get(b"modify",b"none")
	if   action == b"none"  : disabled = True
	elif action == b"modify": disabled = False 
	elif action == b"save"  : 
		disabled = True
		del request.params[b"modify"]
		config.update(request.params)
		config.save()
		await asyncNotify(token=config.token, user=config.user, message = b"Pushover config modified")

	if disabled:
		submit = Submit(text=b"Modify")
		value = b'modify'
	else:
		submit = Submit(text=b"Save")
		value = b'save'

	page = mainPage(
		content=[Br(),Container([\
					Card([\
						Form([\
							Br(),
							Title3(text=b"Notification configuration"),
							Edit(text=b"User",  name=b"user",  placeholder=b"Enter pushover user",  type=b"password", value=config.user,  disabled=disabled),
							Edit(text=b"Token", name=b"token", placeholder=b"Enter pushover token", type=b"password", value=config.token, disabled=disabled),
							Input (text=b"modify" , name=b"modify", type=b"hidden", value=value),
							submit,
						]),
					])
					,Br()
					,Link(href=b"https://pushover.net", text=b"See pushover website"),
				])
			], title=args["title"], active=args["index"], request=request, response=response)

	await response.sendPage(page)
