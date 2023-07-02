# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Presence simulator that plays sounds in the absence of the occupants of a dwelling """
import plugins.presencesimu.dfplayer
import server.presence
import tools.tasking
import uasyncio
import time

class PresenceSimu:
	""" Presence simulator that plays sounds in the absence of the occupants of a dwelling """
	presencesimu = None
	def __init__(self):
		""" Create presence simulator """
		self.dfplayer = plugins.presencesimu.dfplayer.DFPlayer(display=True)
		self.last_play = 0

	async def task(self, **kwargs):
		""" Task presence simulator """
		if server.presence.Presence.activated:
			if server.presence.Presence.is_detected() is False:
				if self.last_play == 0:
					print("Absence detected")
				if self.last_play + 200 < time.time():
					self.last_play = time.time()
					self.dfplayer.play_next()
				else:
					response = self.dfplayer.receive()
					if response is not None:
						self.dfplayer.play_next()
			else:
				if self.last_play != 0:
					print("Presence detected")
					self.dfplayer.stop()
					self.last_play = 0
		await uasyncio.sleep(2)

	@staticmethod
	def start(**kwargs):
		""" Start presence simulator task """
		if PresenceSimu.presencesimu is None:
			PresenceSimu.presencesimu = PresenceSimu()
		tools.tasking.Tasks.create_monitor(PresenceSimu.presencesimu.task, **kwargs)

