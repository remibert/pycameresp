# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to change the login password """
from htmltemplate import *
from tools import useful
from server import User, Sessions

class PasswordPage:
	""" Html page of password """
	@staticmethod
	def change(request, response):
		""" Change the password page """
		User.init()
		newPassword = request.params.get(b"newpassword", None)
		if newPassword != None:
			res = User.change(request.params.get(b"user", b""), request.params.get(b"currentpassword", b""), request.params.get(b"newpassword"), request.params.get(b"renewpassword"))
			if res == True:
				return [Br(),AlertSuccess(text=b"Password changed")]
			elif res == None:
				return PasswordPage.changePage(alert=b"Passwords not equals")
			else:
				return PasswordPage.changePage(alert=b"Wrong user or password")
		else:
			return PasswordPage.changePage()

	@staticmethod
	def loginPage(alert=None):
		""" Login password page """
		return PasswordPage.getDialog([Edit(text=b"User", name=b"loginuser"),Edit(text=b"Password", type=b"password", name=b"loginpassword")], b"Login", alert)

	@staticmethod
	def changePage(alert=None):
		""" Change the password page """
		if User.isEmpty():
			part = [Edit(text=b"Create user name",     name=b"user"),]
		else:
			part = [\
				Edit(text=b"Enter user name",          name=b"user"),
				Edit(text=b"Current password",   type=b"password", name=b"currentpassword")]

		part += [\
			Edit(text=b"New password",     type=b"password", name=b"newpassword"),
			Edit(text=b"Repeat new password",     type=b"password", name=b"renewpassword")]

		return PasswordPage.getDialog(part, b"Change password", alert)

	@staticmethod
	def getDialog(content, submit ,alert = None):
		""" Common dialog of login password page """
		if alert != None: alert = AlertError(text=alert), Br()
		return [Br(),Container([alert,Card([Form([Br(),content,Submit(text=submit)], method=b"post")])])]

	@staticmethod
	def login(request, response, duration):
		""" Login page """
		User.init()
		if Sessions.check(request.getCookie(b"session")) == False:
			if User.check(request.params.get(b"loginuser",b""), request.params.get(b"loginpassword",b"")):
				response.setCookie(b"session",Sessions.create(duration),duration)
			else:
				return PasswordPage.loginPage(None if request.params.get(b"loginpassword",None) == None else b"Wrong user or password")
		return None
