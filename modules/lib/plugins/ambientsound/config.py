# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Function define the configuration of the ambient sound """
# pylint:disable=anomalous-unicode-escape-in-string
import time
import tools.jsonconfig
import tools.strings
import tools.date

class AmbientTimeConfig(tools.jsonconfig.JsonConfig):
	""" Ambient time configuration """
	def __init__(self):
		""" Constructor """
		tools.jsonconfig.JsonConfig.__init__(self)
		self.start_time = 0
		self.end_time   = 0

class AmbientSoundConfig(tools.jsonconfig.JsonConfig):
	""" Ambient sound configuration """
	config = None
	last_get_config = 0
	def __init__(self):
		""" Constructor """
		tools.jsonconfig.JsonConfig.__init__(self)
		self.time_slots = []

	def append(self, time_slot):
		""" Add new time slot in the list """
		found = False
		time_slot = tools.strings.tobytes(time_slot)
		for current in self.time_slots:
			if current[b"start_time"] == time_slot.start_time and current[b"end_time"]   == time_slot.end_time:
				found = True
				break
		if found is False:
			self.time_slots.append(tools.strings.tobytes(time_slot.__dict__))

	def get(self, index):
		""" Return the time slot at the index """
		try:
			return self.time_slots[int(index)]
		except:
			return None

	def remove(self, index):
		""" Remove the time slot at the index """
		try:
			del self.time_slots[int(index)]
		except:
			pass

	def is_activated(self):
		""" Indicates if the ambient sound must be activated """
		result = False
		hour,minute,second = tools.date.local_time(time.time())[3:6]
		current_time = (hour * 3600) + (minute * 60) + second
		for time_slot in self.time_slots:
			if current_time >= time_slot[b"start_time"] and current_time <= time_slot[b"end_time"]:
				result = True
				break
		return result

	@staticmethod
	def get_config():
		""" Return the singleton configuration """
		if AmbientSoundConfig.config is None:
			AmbientSoundConfig.config = AmbientSoundConfig()
			AmbientSoundConfig.config.load()

		AmbientSoundConfig.config.refresh()
		return AmbientSoundConfig.config
