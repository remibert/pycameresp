# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Function define the configuration of the electric meter """
# pylint:disable=anomalous-unicode-escape-in-string
from tools                 import jsonconfig, strings

class RateConfig(jsonconfig.JsonConfig):
	""" Kwh rate configuration """
	def __init__(self):
		""" Constructor """
		jsonconfig.JsonConfig.__init__(self)

		self.name = b""
		self.price = 0.0
		self.currency = b""
		self.validity_date = 0

class RatesConfig(jsonconfig.JsonConfig):
	""" Rates list per kwh """
	def __init__(self):
		""" Constructor """
		jsonconfig.JsonConfig.__init__(self)
		self.rates = []

	def append(self, rate):
		""" Add new rate in the list """
		found = False
		rate = strings.tobytes(rate)
		for current in self.rates:
			if current[b"name"] == strings.tobytes(rate.name) and current[b"validity_date"] == strings.tobytes(rate.validity_date):
				found = True
				current[b"currency"] = strings.tobytes(rate.currency)
				current[b"price"] = rate.price
				break
		if found is False:
			self.rates.append(strings.tobytes(rate.__dict__))

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
			if day >= rate[b"validity_date"]:
				# If the same rate already found
				if rate[b"name"] in result:
					# If the rate already found is older than the current rate
					if result[rate[b"name"]][b"validity_date"] < rate[b"validity_date"]:
						# Replace by the current rate
						result[rate[b"name"]] = rate
				else:
					# Keep the current rate
					result[rate[b"name"]] = rate
		return result

class TimeSlotConfig(jsonconfig.JsonConfig):
	""" Time slot configuration """
	def __init__(self):
		""" Constructor """
		jsonconfig.JsonConfig.__init__(self)
		self.rate       = b""
		self.start_time = 0
		self.end_time   = 0
		self.color      = b""

class TimeSlotsConfig(jsonconfig.JsonConfig):
	""" Time slots list """
	def __init__(self):
		""" Constructor """
		jsonconfig.JsonConfig.__init__(self)
		self.time_slots = []

	def append(self, time_slot):
		""" Add new time slot in the list """
		found = False
		time_slot = strings.tobytes(time_slot)
		for current in self.time_slots:
			if current[b"start_time"] == time_slot.start_time and current[b"end_time"]   == time_slot.end_time:
				current[b"color"] = time_slot.color
				current[b"rate"]  = time_slot.rate
				found = True
				break
		if found is False:
			self.time_slots.append(strings.tobytes(time_slot.__dict__))

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
			result = [{b'rate': b'', b'start_time': 0, b'end_time': 86340, b'color': b'#5498e0', b'price': 0, b'currency': b'not initialized'}]
		else:
			result = self.time_slots[:]
			for time_slot in result:
				time_slot[b"price"]    = rates[time_slot[b"rate"]][b"price"]
				time_slot[b"currency"] = rates[time_slot[b"rate"]][b"currency"]
		return result
