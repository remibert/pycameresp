# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Ambient sound that plays sounds in the absence of the occupants of a dwelling """
import time
import uasyncio
import plugins.ambientsound.dfplayer
import plugins.ambientsound.config
import server.presence
import server.notifier
import tools.tasking
import tools.system

class AmbientSound:
	""" Ambient sound that plays sounds in the absence of the occupants of a dwelling """
	ambientsound = None
	SLOW_POLLING = 15#67
	FAST_POLLING = 3

	def __init__(self):
		""" Create ambient sound """
		self.dfplayer = plugins.ambientsound.dfplayer.DFPlayer()#display=True)
		self.last_play = 0
		self.last_receive = 0
		self.config = plugins.ambientsound.config.AmbientSoundConfig()
		self.last_action = time.time()
		self.error_count = 0

	async def task(self, **kwargs):
		""" Task ambient sound """
		activated = False

		# If presence detection activated
		if server.presence.Presence.activated:
			# Get ambient sound config
			config = plugins.ambientsound.config.AmbientSoundConfig().get_config()

			# If ambient sound can be played now
			if config.is_activated():
				activated = True

				# If the home is empty
				if server.presence.Presence.is_detected():
					activated = False

		# If sound must be played
		if activated:
			play_next = True
			play_first = False

			# If the sound has been going on for too long
			if self.last_play + 120 < time.time() or self.last_play == 0:
				play_first = True
			else:
				# Get the player result
				response = self.dfplayer.receive()

				# If the sound terminated
				if response is not None:
					status, value = response
					self.last_receive = time.time()
					if status != plugins.ambientsound.dfplayer.PLAY_ENDED:
						tools.logger.syslog("Ambient sound, player problem %02X, %d"%(status, value))
						play_first = True
						self.error_count += 1
					else:
						self.error_count = 0
				else:
					play_next = False

			if self.error_count > 30:
				server.notifier.Notifier.notify(message=plugins.ambientsound.lang.player_problem)
				if self.error_count > 40:
					tools.system.reboot("Reboot device after player problem")

			# If the play first selected
			if play_first:
				await uasyncio.sleep(0.3)
				self.dfplayer.play_track(0,0)
				await uasyncio.sleep(0.5)

			# If the next sound must be played
			if play_next:
				if self.last_play == 0:
					tools.logger.syslog("Ambient sound start")
					self.last_receive = time.time()
				elif self.last_receive + 1200 < time.time() :
					server.notifier.Notifier.notify(message=plugins.ambientsound.lang.player_problem)
					await uasyncio.sleep(15)
					tools.system.reboot("Reboot device after no response player")

				# Play next sound
				self.dfplayer.play_next()
				await uasyncio.sleep(0.5)
				self.last_play = time.time()
			await uasyncio.sleep(AmbientSound.FAST_POLLING)
		else:
			# If sound is played
			if self.last_play != 0:
				tools.logger.syslog("Ambient sound stop")
				self.last_play = 0
			await uasyncio.sleep(AmbientSound.SLOW_POLLING)

	@staticmethod
	def start(**kwargs):
		""" Start ambient sound task """
		if AmbientSound.ambientsound is None:
			AmbientSound.ambientsound = AmbientSound()
		tools.tasking.Tasks.create_monitor(AmbientSound.ambientsound.task, **kwargs)
