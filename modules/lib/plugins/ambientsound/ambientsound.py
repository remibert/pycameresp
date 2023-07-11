# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Ambient sound that plays sounds in the absence of the occupants of a dwelling """
import uasyncio
import plugins.ambientsound.dfplayer
import plugins.ambientsound.config
import plugins.ambientsound.lang
import server.presence
import server.notifier
import tools.tasking
import tools.system

class AmbientSound:
	""" Ambient sound that plays sounds in the absence of the occupants of a dwelling """
	ambientsound = None
	SLOW_POLLING = 17 * 1000
	FAST_POLLING =  2 * 1000
	DURATION_SOUND = 200
	MAX_TOO_LONG_SOUND = 10

	STATE_STOPPED   = 0
	STATE_PLAYING   = 1

	def __init__(self):
		""" Create ambient sound """
		self.dfplayer = plugins.ambientsound.dfplayer.DFPlayer()#display=True)
		self.config = plugins.ambientsound.config.AmbientSoundConfig()
		self.loop = 0
		self.loop_start_play = 0
		self.state = AmbientSound.STATE_STOPPED
		self.too_long = 0

	async def dfplayer_simulator(self, **kwargs):
		""" Simulate response from dfplayer """
		while True:
			await uasyncio.sleep(15)
			self.dfplayer.uart.simul_receive(b"\x7E\xFF\x06\x40\x00\x00\x06\xB5\xFE\xEF")
			await uasyncio.sleep(15)
			self.dfplayer.uart.simul_receive(b"\x7E\xFF\x06\x3D\x00\x00\x04\xFE\xBA\xEF")

	def is_active(self):
		""" Indicates if the ambient sound is active """
		result = False
		# If presence detection activated
		if server.presence.Presence.activated:
			# Get ambient sound config
			config = plugins.ambientsound.config.AmbientSoundConfig().get_config()

			# If ambient sound can be played now
			if config.is_activated():
				# If the home is empty
				if server.presence.Presence.is_detected() is False:
					result = True
		return result

	async def state_stopped(self):
		""" State ambient sound stopped """
		# If the ambient sound is active
		if self.is_active():
			tools.logger.syslog("Ambient sound start")
			self.dfplayer.play_next()
			self.loop_start_play = self.loop
			self.too_long = 0
			self.state = AmbientSound.STATE_PLAYING
		else:
			await tools.tasking.Tasks.wait_resume(duration=AmbientSound.SLOW_POLLING, name="ambientsound")

	async def state_playing(self):
		""" State ambient sound playing """
		await tools.tasking.Tasks.wait_resume(duration=AmbientSound.FAST_POLLING, name="ambientsound")

		# If the ambient sound is active
		if self.is_active() is True:
			# Get the player result
			response = self.dfplayer.receive()

			# If response received
			if response is not None:
				command, value = response
				# If sound ended
				if (command == plugins.ambientsound.dfplayer.PLAY_ENDED) or \
				   (command == plugins.ambientsound.dfplayer.QUERY_STATUS and value == 0):
					self.dfplayer.play_next()
					self.loop_start_play = self.loop
					self.too_long = 0
			elif (self.loop % 5) == 4:
				self.dfplayer.get_status()

			# If the sound too long
			if ((self.loop - self.loop_start_play) * AmbientSound.FAST_POLLING // 1000) > AmbientSound.DURATION_SOUND:
				if self.too_long == 0:
					tools.logger.syslog("Ambient sound too long")
				self.too_long += 1

				if self.too_long > AmbientSound.MAX_TOO_LONG_SOUND:
					tools.logger.syslog("Too much ambient sound too long")
					# Duration to let the event go
					await uasyncio.sleep(15)
					tools.system.reboot("Too much ambient sound too long")
		else:
			# Stop ambient sound
			tools.logger.syslog("Ambient sound stop")
			self.state = AmbientSound.STATE_STOPPED

	async def task(self, **kwargs):
		""" Task ambient sound """
		while True:
			if self.state == AmbientSound.STATE_STOPPED:
				await self.state_stopped()
			else:
				await self.state_playing()
			self.loop += 1

	@staticmethod
	def start(**kwargs):
		""" Start ambient sound task """
		if AmbientSound.ambientsound is None:
			AmbientSound.ambientsound = AmbientSound()
		tools.tasking.Tasks.create_monitor(AmbientSound.ambientsound.task, **kwargs)
		if tools.filesystem.ismicropython() is False:
			tools.tasking.Tasks.create_monitor(AmbientSound.ambientsound.dfplayer_simulator)
