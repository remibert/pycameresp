# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class used to manage a username and a password """
from tools import useful,jsonconfig

EMPTY_PASSWORD = b"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" # empty password

class UserConfig(jsonconfig.JsonConfig):
	""" User configuration """
	def __init__(self):
		""" Constructor """
		jsonconfig.JsonConfig.__init__(self)
		self.user = b""
		self.password = EMPTY_PASSWORD
		if self.load() == False:
			self.save()

class User:
	""" Singleton class to manage the user. Only one user can be defined """
	instance = None
	loginState = [None]

	@staticmethod
	def init():
		""" Constructor """
		if User.instance == None:
			User.instance = UserConfig()

	@staticmethod
	def getLoginState():
		""" Indicates if login success or failed detected """
		result = User.loginState[0]
		User.loginState[0] = None
		return result

	@staticmethod
	def check(user, password):
		""" Check the user and password """
		User.init()
		if User.instance.user == b"":
			return True
		elif user == User.instance.user:
			if useful.getHash(password) == User.instance.password:
				User.loginState[0] = True
				return True
			else:
				User.loginState[0] = False
				useful.logError("Login failed, wrong password for user '%s'"%useful.tostrings(user))
		else:
			User.loginState[0] = False
			if user != b"":
				useful.logError("Login failed, unkwnon user '%s'"%useful.tostrings(user))
		return False

	@staticmethod
	def isEmpty():
		""" If no user defined """
		User.init()
		if User.instance.user == b"":
			return True
		else:
			return False

	@staticmethod
	def getUser():
		""" Get the user """
		User.init()
		return User.instance.user

	@staticmethod
	def change(user, currentPassword, newPassword, reNewPassword):
		""" Change the user and password, check if the password is correct before to do this """
		User.init()

		if User.check(user, currentPassword):
			if newPassword == reNewPassword:
				if newPassword == b"":
					User.instance.user     = b""
					User.instance.password = EMPTY_PASSWORD
				else:
					User.instance.user     = user
					User.instance.password = useful.getHash(newPassword)
				User.instance.save()
				return True
			else:
				return None
		return False
