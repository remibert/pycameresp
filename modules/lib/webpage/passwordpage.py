# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to change the login password """
from htmltemplate import *
from tools import useful, lang
from server.user import User
from server.sessions import Sessions

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
				return [Br(),AlertSuccess(text=lang.password_changed)]
			elif res == None:
				return PasswordPage.changePage(alert=lang.passwords_not_equals)
			else:
				return PasswordPage.changePage(alert=lang.wrong_user_or)
		else:
			return PasswordPage.changePage()

	@staticmethod
	def loginPage(alert=None):
		""" Login password page """
		return PasswordPage.getDialog([Edit(text=lang.user, name=b"loginuser"),Edit(text=lang.password, type=b"password", name=b"loginpassword")], lang.login, alert, True)

	@staticmethod
	def changePage(alert=None):
		""" Change the password page """
		if User.isEmpty():
			part = [Edit(text=lang.create_user_name,     name=b"user"),]
		else:
			part = [\
				Edit(text=lang.enter_user_name,          name=b"user"),
				Edit(text=lang.current_password,   type=b"password", name=b"currentpassword")]

		part += [\
			Edit(text=lang.new_password,     type=b"password", name=b"newpassword"),
			Edit(text=lang.repeat_new_password,     type=b"password", name=b"renewpassword")]

		return PasswordPage.getDialog(part, lang.modify_password, alert)

	@staticmethod
	def getDialog(content, submit ,alert = None, modal=False):
		""" Common dialog of login password page """
		if alert != None: alert = AlertError(text=alert)
		dialog = [alert, Form([content, Submit(text=submit)], method=b"post")]
		if modal:
			dialog = Modal(dialog)
		return [dialog]

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
