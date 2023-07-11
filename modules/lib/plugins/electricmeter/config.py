# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Function define the configuration of the electric meter """
# pylint:disable=anomalous-unicode-escape-in-string
import tools.jsonconfig
import tools.strings

class RateConfig(tools.jsonconfig.JsonConfig):
	""" Kwh rate configuration """
	def __init__(self):
		""" Constructor """
		tools.jsonconfig.JsonConfig.__init__(self)

		self.name = b""
		self.price = 0.0
		self.currency = b""
		self.validity_date = 0

class RatesConfig(tools.jsonconfig.JsonConfig):
	""" Rates list per kwh """
	config = None
	def __init__(self):
		""" Constructor """
		tools.jsonconfig.JsonConfig.__init__(self)
		_ = RateConfig() # <- This line is REQUIRED for deserialization to work
		self.rates = []

	def append(self, rate):
		""" Add new rate in the list """
		found = False
		for current in self.rates:
			if current.name == rate.name and current.validity_date == rate.validity_date:
				found = True
				break
		if found is False:
			self.rates.append(rate)

	def get(self, index):
		""" Return the rate at the index """
		try:
			return self.rates[int(index)]
		except:
			return None

	def remove(self, index):
		""" Remove the rate at the index """
		try:
			del self.rates[int(index)]
		except:
			pass

	def search_rates(self, day):
		""" Find the current rate """
		result = {}
		day = int(day)
		for rate in self.rates:
			# If the rate is valid for the current date
			if day >= rate.validity_date:
				# If the same rate already found
				if rate.name in result:
					# If the rate already found is older than the current rate
					if result[rate.name].validity_date < rate.validity_date:
						# Replace by the current rate
						result[rate.name] = rate
				else:
					# Keep the current rate
					result[rate.name] = rate
		return result

	@staticmethod
	def get_config():
		""" Return the singleton configuration """
		if RatesConfig.config is None:
			RatesConfig.config = RatesConfig()
			RatesConfig.config.load()
		return RatesConfig.config

class TimeSlotConfig(tools.jsonconfig.JsonConfig):
	""" Time slot configuration """
	def __init__(self):
		""" Constructor """
		tools.jsonconfig.JsonConfig.__init__(self)
		self.rate       = b""
		self.start_time = 0
		self.end_time   = 86340
		self.color      = b"5498e0"
		self.currency   = b"not initialized"
		self.price      = 0.0

class TimeSlotsConfig(tools.jsonconfig.JsonConfig):
	""" Time slots list """
	config = None
	def __init__(self):
		""" Constructor """
		tools.jsonconfig.JsonConfig.__init__(self)
		_ = TimeSlotConfig() # <- This line is REQUIRED for deserialization to work
		self.time_slots = []

	def append(self, time_slot):
		""" Add new time slot in the list """
		found = False
		for current in self.time_slots:
			if current.start_time == time_slot.start_time and current.end_time == time_slot.end_time:
				current.currency = time_slot.currency
				current.color    = time_slot.color
				current.price    = time_slot.price
				current.rate     = time_slot.rate
				found = True
				break
		if found is False:
			self.time_slots.append(time_slot)

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

	def get_prices(self, rates):
		""" Return the list of prices according to the day """
		if rates == {}:
			result = [TimeSlotConfig()]
		else:
			result = self.time_slots[:]
			for time_slot in result:
				time_slot.price    = rates[time_slot.rate].price
				time_slot.currency = rates[time_slot.rate].currency
		return result

	@staticmethod
	def get_config():
		""" Return the singleton configuration """
		if TimeSlotsConfig.config is None:
			TimeSlotsConfig.config = TimeSlotsConfig()
			TimeSlotsConfig.config.load()
		return TimeSlotsConfig.config

	@staticmethod
	def get_cost(day):
		""" Get the cost according to the day selected """
		time_slots = TimeSlotsConfig.get_config()
		rates      = RatesConfig.get_config()
		return time_slots.get_prices(rates.search_rates(day))

	@staticmethod
	def create_empty_slot(size):
		""" Create empty time slot """
		time_slots = TimeSlotsConfig()
		time_slots.load()
		slot_pulses = {}
		index = 0
		while True:
			time_slot = time_slots.get(index)
			if time_slot is None:
				break
			slot_pulses[(time_slot.start_time, time_slot.end_time)] = [0]*size
			index += 1
		if len(slot_pulses) == 0:
			slot_pulses[(0,1439*60)] = [0]*size
		return slot_pulses

class GeolocationConfig(tools.jsonconfig.JsonConfig):
	""" Geolocation configuration """
	config = None
	def __init__(self):
		""" Constructor """
		tools.jsonconfig.JsonConfig.__init__(self)
		self.latitude  = 44.93
		self.longitude = 4.87

	@staticmethod
	def get_config():
		""" Return the singleton configuration """
		if GeolocationConfig.config is None:
			GeolocationConfig.config = GeolocationConfig()
			GeolocationConfig.config.load()
		return GeolocationConfig.config
