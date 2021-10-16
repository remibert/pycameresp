# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class used to store http connection sessions, it is useful if you define
an user and password, on your site """
import time
from tools import useful, encryption

class Sessions:
	""" Class manage an http sessions """
	sessions = []

	@staticmethod
	def create(duration):
		""" Create new session """
		session = encryption.gethash(useful.date_to_bytes())
		Sessions.sessions.append((session, time.time() + duration))
		return session

	@staticmethod
	def check(session):
		""" Check if the session not expired """
		result = False
		if session is not None:
			for sessionId, expiration in Sessions.sessions:
				if sessionId == session:
					result = True
					break
		Sessions.purge()
		return result

	@staticmethod
	def purge():
		""" Purge older sessions (only expired) """
		current_time = time.time()
		for sessionId, expiration in Sessions.sessions:
			if expiration < current_time:
				Sessions.sessions.remove((sessionId, expiration))

	@staticmethod
	def remove(sessionIdRemove):
		""" Remove session """
		for sessionId, expiration in Sessions.sessions:
			if sessionId == sessionIdRemove:
				Sessions.sessions.remove((sessionId, expiration))
