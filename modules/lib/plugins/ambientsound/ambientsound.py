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
	SLOW_POLLING = 11 * 1000
	FAST_POLLING =  2 * 1000
	DURATION_SOUND = 200
	REBOOT_FAULT = 64
	REOPEN_FAULT = 4

	STATE_STOPPED   = 0
	STATE_PLAYING   = 1

	def __init__(self):
		""" Create ambient sound """
		self.open_player()
		self.config = plugins.ambientsound.config.AmbientSoundConfig()
		self.loop = 0
		self.last_play = 0
		self.fault = 0
		self.state = AmbientSound.STATE_STOPPED
		self.last_open = 0

	def open_player(self):
		""" Open sound player """
		if hasattr(AmbientSound,"dfplayer") is True:
			del self.dfplayer
		self.dfplayer = plugins.ambientsound.dfplayer.DFPlayer()#display=True)

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
			self.play_next()
		else:
			# Clean up data received
			self.dfplayer.receive()
			await tools.tasking.Tasks.wait_resume(duration=AmbientSound.SLOW_POLLING, name="ambientsound")

	def play_next(self):
		""" Play next sound """
		self.dfplayer.play_next()
		self.last_play = self.loop
		self.state = AmbientSound.STATE_PLAYING

	def increase_fault(self):
		""" Increase the fault counter """
		self.fault += 1

	def clear_fault(self):
		""" Clear the fault counter """
		self.fault = 0

	async def get_status(self, ask_status=True):
		""" Ask status and wait response 
		return True if sound ended, False if sound playing, None if error """
		result = None
		no_response = True

		if ask_status:
			self.dfplayer.get_status()

		for i in range(6):
			# Get the player result
			response = self.dfplayer.receive()

			# If response received
			if response is not None:
				no_response = False
				command, value = response
				# If sound ended
				if (command == plugins.ambientsound.dfplayer.PLAY_ENDED) or \
				   (command == plugins.ambientsound.dfplayer.QUERY_STATUS and value == 0):
					self.clear_fault()
					result = True
					break
				elif (command == plugins.ambientsound.dfplayer.QUERY_STATUS and value != 0):
					self.clear_fault()
					result = False
					break
				elif (command == plugins.ambientsound.dfplayer.ERR_FILE):
					self.increase_fault()
					result = True
					break
			else:
				await uasyncio.sleep_ms(500)

		# No response received
		if no_response and ask_status:
			self.increase_fault()
			result = None
		return result

	async def state_playing(self):
		""" State ambient sound playing """
		await tools.tasking.Tasks.wait_resume(duration=AmbientSound.FAST_POLLING, name="ambientsound")

		# If the ambient sound is active
		if self.is_active() is True:
			if self.loop % 5 == 4:
				ask_status = True
			else:
				ask_status = False
			ended = await self.get_status(ask_status=ask_status)

			if ended is True:
				self.play_next()

			too_long_duration = ((self.loop - self.last_play) * AmbientSound.FAST_POLLING // 1000) > AmbientSound.DURATION_SOUND

			# If fault quantity is not too important
			if self.fault % AmbientSound.REOPEN_FAULT == (AmbientSound.REOPEN_FAULT -1):
				# Close and reopen uart to test if fault can be resolved
				self.open_player()
				await uasyncio.sleep_ms(500)

				# Ask status
				ended = await self.get_status(ask_status=True)

				# If sound ended
				if ended is True:
					# Play next sound
					await uasyncio.sleep_ms(500)
					self.play_next()
			# If the sound failure detected
			elif too_long_duration or self.fault >= AmbientSound.REBOOT_FAULT:
				# If there is no user activity
				if tools.tasking.Tasks.is_slow_down() is False:
					# Reboot required
					server.notifier.Notifier.notify(message="Ambient sound fault")
					await uasyncio.sleep(15)
					tools.system.reboot("Ambient sound fault")
		else:
			# Stop ambient sound
			tools.logger.syslog("Ambient sound stop")
			self.dfplayer.stop()
			self.state = AmbientSound.STATE_STOPPED

	async def task(self, **kwargs):
		""" Task ambient sound """
		while True:
			self.loop += 1
			if self.state == AmbientSound.STATE_STOPPED:
				await self.state_stopped()
			else:
				await self.state_playing()

	@staticmethod
	def start(**kwargs):
		""" Start ambient sound task """
		if AmbientSound.ambientsound is None:
			AmbientSound.ambientsound = AmbientSound()
		tools.tasking.Tasks.create_monitor(AmbientSound.ambientsound.task, **kwargs)
		if tools.filesystem.ismicropython() is False:
			tools.tasking.Tasks.create_monitor(AmbientSound.ambientsound.dfplayer_simulator)

	async def dfplayer_simulator(self, **kwargs):
		""" Simulate response from dfplayer """
		while True:
			await uasyncio.sleep(15)
			self.dfplayer.uart.simul_receive(b"\x7E\xFF\x06\x40\x00\x00\x06\xB5\xFE\xEF")
			await uasyncio.sleep(15)
			self.dfplayer.uart.simul_receive(b"\x7E\xFF\x06\x3D\x00\x00\x04\xFE\xBA\xEF")
