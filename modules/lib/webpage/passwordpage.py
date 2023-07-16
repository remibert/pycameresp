# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Function define the web page to change the login password """
from htmltemplate import *
import server.user
import server.sessions
import tools.lang

class PasswordPage:
	""" Html page of password """
	@staticmethod
	def change(request, response):
		""" Change the password page """
		server.user.User.init()
		new_password = request.params.get(b"new_password", None)
		if new_password is not None:
			res = server.user.User.change(request.params.get(b"user", b""), request.params.get(b"current_password", b""), request.params.get(b"new_password"), request.params.get(b"renew_password"))
			if res is True:
				return [AlertSuccess(text=tools.lang.password_changed)]
			elif res is None:
				return PasswordPage.change_page(alert=tools.lang.passwords_not_equals)
			else:
				return PasswordPage.change_page(alert=tools.lang.wrong_user_or)
		else:
			return PasswordPage.change_page()

	@staticmethod
	def login_page(alert=None, action=b""):
		""" Login password page """
		return PasswordPage.get_dialog([
			Edit(text=tools.lang.user, name=b"login_user"),
			Edit(text=tools.lang.password, type=b"password", name=b"login_password"),
			Switch(text=tools.lang.remember_me, name=b"remember_me", checked=False)
			],
			tools.lang.login, alert=alert, modal=True, action=action)

	@staticmethod
	def change_page(alert=None):
		""" Change the password page """
		if server.user.User.is_empty():
			part = [Edit(text=tools.lang.create_user_name,     name=b"user"),]
		else:
			part = [\
				Edit(text=tools.lang.enter_user_name,          name=b"user"),
				Edit(text=tools.lang.current_password,   type=b"password", name=b"current_password")]

		part += [\
			Edit(text=tools.lang.new_password,     type=b"password", name=b"new_password"),
			Edit(text=tools.lang.repeat_new_password,     type=b"password", name=b"renew_password")]

		return PasswordPage.get_dialog(part, tools.lang.modify_password, alert)

	@staticmethod
	def get_dialog(content, submit ,alert = None, modal=False, action=b""):
		""" Common dialog of login password page """
		if alert is not None:
			alert = AlertError(text=alert)
		dialog = [alert, Div([content, Submit(text=submit)], action=action)]
		if modal:
			dialog = Div(Modal(dialog),class_=b"modal-sm")
		return Form([dialog],method=b"post")

	@staticmethod
	def login(request, response, duration=0):
		""" Login page """
		server.user.User.init()
		if server.sessions.Sessions.check(request.get_cookie(b"session")) is False:
			if server.user.User.check(request.params.get(b"login_user",b""), request.params.get(b"login_password",b"")):
				if duration > 0:
					response.set_cookie(b"session",server.sessions.Sessions.create(duration, request.params.get(b"remember_me",b"")),duration, http_only=True)
			else:
				return PasswordPage.login_page(None if request.params.get(b"login_password",None) is None else tools.lang.wrong_user_or, action=b"/")
		return None

	@staticmethod
	def logout(request, response):
		""" Logout page """
		server.user.User.init()
		server.sessions.Sessions.remove(request.get_cookie(b"session"))
