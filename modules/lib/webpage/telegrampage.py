# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to configure the telegram notifications """
from server.httpserver import HttpServer
from htmltemplate import *
from webpage import *
from server.telegram import *

@HttpServer.addRoute(b'/telegram', title=b"Telegram", index=16)
async def telegram(request, response, args):
	""" Function define the web page to configure the telegram notifications """
	config = TelegramConfig()
	disabled, action, submit = manageDefaultButton(request, config)
	if action == b"save":
		await asyncNotify(chatId=config.chatId, botToken=config.botToken, message = b"telegram notification %s"%(b"on" if config.activated else b"off"))
	if disabled:
		type = b"password"
	else:
		type = b""
	page = mainFrame(request, response, args,b"Notification configuration",
		Switch(text=b"Activated", name=b"activated", checked=config.activated, disabled=disabled),Br(),
		Edit(text=b"Bot token",  name=b"botToken",  placeholder=b"Enter telegram bot token",  type=type, value=config.botToken,  disabled=disabled),
		Edit(text=b"Chat id", name=b"chatId", placeholder=b"Enter telegram chat id", type=type, value=config.chatId, disabled=disabled),
		submit,
		Br(), Br(), Link(href=b"https://telegram.org", text=b"See telegram website"))

	await response.sendPage(page)
