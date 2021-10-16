# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the web page to change the login password """
from htmltemplate import *
from server.user import User
from server.sessions import Sessions
from tools import useful, lang

class PasswordPage:
	""" Html page of password """
	@staticmethod
	def change(request, response):
		""" Change the password page """
		User.init()
		new_password = request.params.get(b"new_password", None)
		if new_password is not None:
			res = User.change(request.params.get(b"user", b""), request.params.get(b"current_password", b""), request.params.get(b"new_password"), request.params.get(b"renew_password"))
			if res is True:
				return [Br(),AlertSuccess(text=lang.password_changed)]
			elif res is None:
				return PasswordPage.change_page(alert=lang.passwords_not_equals)
			else:
				return PasswordPage.change_page(alert=lang.wrong_user_or)
		else:
			return PasswordPage.change_page()

	@staticmethod
	def login_page(alert=None, action=b""):
		""" Login password page """
		return PasswordPage.get_dialog([Edit(text=lang.user, name=b"login_user"),Edit(text=lang.password, type=b"password", name=b"login_password")], lang.login, alert=alert, modal=True, action=action)

	@staticmethod
	def change_page(alert=None):
		""" Change the password page """
		if User.is_empty():
			part = [Edit(text=lang.create_user_name,     name=b"user"),]
		else:
			part = [\
				Edit(text=lang.enter_user_name,          name=b"user"),
				Edit(text=lang.current_password,   type=b"password", name=b"current_password")]

		part += [\
			Edit(text=lang.new_password,     type=b"password", name=b"new_password"),
			Edit(text=lang.repeat_new_password,     type=b"password", name=b"renew_password")]

		return PasswordPage.get_dialog(part, lang.modify_password, alert)

	@staticmethod
	def get_dialog(content, submit ,alert = None, modal=False, action=b""):
		""" Common dialog of login password page """
		if alert is not None:
			alert = AlertError(text=alert)
		dialog = [alert, Form([content, Submit(text=submit)], method=b"post", action=action)]
		if modal:
			dialog = Modal(dialog)
		return [dialog]

	@staticmethod
	def login(request, response, duration):
		""" Login page """
		User.init()
		if Sessions.check(request.get_cookie(b"session")) is False:
			if User.check(request.params.get(b"login_user",b""), request.params.get(b"login_password",b"")):
				response.set_cookie(b"session",Sessions.create(duration),duration)
			else:
				return PasswordPage.login_page(None if request.params.get(b"login_password",None) is None else lang.wrong_user_or, action=b"/")
		return None

	@staticmethod
	def logout(request, response):
		""" Logout page """
		User.init()
		Sessions.remove(request.get_cookie(b"session"))
		return PasswordPage.login_page()
