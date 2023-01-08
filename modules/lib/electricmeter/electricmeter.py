""" Task to count wh from the electric meter """
import struct
import time
import collections
import uasyncio
import machine
import wifi
from server.server import Server
from electricmeter.config   import TimeSlotsConfig
from electricmeter          import em_lang
from tools import filesystem, date, strings, fnmatch, logger, tasking, info
# pylint:disable=consider-using-f-string
# pylint:disable=consider-iterating-dictionary
# pylint:disable=missing-function-docstring
# pylint:disable=global-variable-not-assigned
# pylint:disable=trailing-whitespace
# pylint:disable=too-many-lines

# Hourly file format :
#  - pulses_per_minute:uint8_t * 24*60

# Daily file format :
#  - (start_time:uint16_t, end_time:uint16_t, pulses_per_day:uint16_t * 31 days) * max_time_slots

# Monthly file format :
#  - (start_time:uint16_t, end_time:uint16_t, pulses_per_month:uint32_t * 12 months) * max_time_slots

PULSE_DIRECTORY = "pulses"
PULSE_HOURLY   = ".hourly"
PULSE_DAILY    = ".daily"
PULSE_MONTHLY  = ".monthly"

class PulseSensor:
	""" Detect wh pulse from electric meter """
	def __init__(self, gpio, min_duration_ns=20_000_000, queue_length=1_500):
		self.pulses = collections.deque((), queue_length)
		self.notifier = uasyncio.Event()
		self.previous_counter = 0
		self.previous_time = time.time_ns()
		self.min_duration_ns = min_duration_ns

		# The use of pcnt counter allows to obtain a better reliability of counting
		self.counter = machine.Counter(0, src=machine.Pin(gpio, mode=machine.Pin.IN), direction=machine.Counter.UP)
		self.counter.filter_ns(self.min_duration_ns)
		self.counter.pause()
		self.counter.value(0)

		self.sensor = machine.Pin(gpio, machine.Pin.IN, machine.Pin.PULL_DOWN)
		self.sensor.irq(handler=self.detected, trigger=machine.Pin.IRQ_RISING)
		self.counter.resume()

	def __del__(self):
		""" Destructor """
		self.sensor.irq(handler=None)
		self.counter.deinit()

	def detected(self, pin):
		""" Callback called when pulse detected """
		pulse_time     = time.time_ns()
		pulse_counter  = self.counter.value()
		if pin.value() == 1:
			# If new pulses detected
			if pulse_counter != self.previous_counter:
				# if the pulse is not too close to the previous one
				if self.previous_time + self.min_duration_ns < pulse_time:
					# If the new value is not a counter overflow
					if pulse_counter > self.previous_counter:
						pulse_quantity = pulse_counter - self.previous_counter
					else:
						pulse_quantity = 1

					# Save the new counter value
					self.previous_counter = pulse_counter

					# Add the current pulse to list
					self.pulses.append((pulse_quantity, pulse_time))

					# Wake up pulse counter
					self.notifier.set()
				else:
					# Ignore previous pulse
					self.previous_counter = pulse_counter

	async def wait(self):
		""" Wait the wh pulses and the returns the list of pulses """
		# Wait pulses
		await self.notifier.wait()

		# Clear notification flag
		self.notifier.clear()
		result = []

		# Empty list of pulses
		while True:
			try:
				result.append(self.pulses.popleft())
			except IndexError:
				break
		return result

	def simulate(self, pulses):
		""" Simulates the flashing led on the electric meter """
		self.sensor.value(1)
		self.counter.value(pulses)
		self.detected(self.sensor)

class HourlyCounter:
	""" Hourly counter of wh consumed """
	counter = None

	def __init__(self, gpio):
		""" Constructor """
		global PULSE_DIRECTORY
		filesystem.makedir(PULSE_DIRECTORY,True)
		self.day    = time.time()
		self.pulses = HourlyCounter.load(HourlyCounter.get_filename(self.day))
		self.last_save = time.time()
		self.watt_hour = 0
		self.previous_pulse_time = None
		self.day_pulses_counter = 0
		self.pulse_sensor = PulseSensor(gpio)
	
	async def manage(self):
		""" Manage the counter """
		# Wait the list of pulses
		pulses = await self.pulse_sensor.wait()
		for pulse_quantity, pulse_time in pulses:
			# If previous pulse registered
			if self.previous_pulse_time is not None:
				# Compute the instant power
				self.watt_hour = 3600 * 1_000_000_000/((pulse_time - self.previous_pulse_time)/pulse_quantity)

			# Increase
			self.day_pulses_counter += pulse_quantity
			self.previous_pulse_time = pulse_time
			hour,minute=date.local_time(pulse_time//1_000_000_000)[3:5]
			day   = pulse_time//1_000_000_000
			minut = hour*60+minute
			self.pulses[minut] += pulse_quantity

			# If day change
			if HourlyCounter.is_same_day(day, self.day) is False:
				# Save day counter
				HourlyCounter.save(HourlyCounter.get_filename(self.day))

				# Clear day pulses counter
				self.day_pulses_counter = 0

				# Load new day if existing or clear counter (manage day light saving)
				self.pulses = self.load(day)
				self.day = day

		# Each ten minutes
		if time.time() > (self.last_save + 67):
			# Save pulses file
			HourlyCounter.save(HourlyCounter.get_filename(self.day))

		# print("%s %.1f wh pulses=%d"%(date.date_to_string(), self.watt_hour, self.day_pulses_counter))
		return True

	@staticmethod
	def is_same_day(day1, day2):
		""" Indicates if the day 1 is equal to day 2"""
		if day1//86400 == day2//86400 or day1 is None or day2 is None:
			return True
		else:
			return False

	@staticmethod
	def get_filename(day=None):
		""" Return the filename according to day """
		global PULSE_DIRECTORY, PULSE_HOURLY
		if day is None:
			day = time.time()
		year,month,day = date.local_time(day)[:3]
		return "%s/%04d-%02d/%04d-%02d-%02d%s"%(PULSE_DIRECTORY, year, month, year, month, day, PULSE_HOURLY)

	@staticmethod
	def save(filename):
		""" Save pulses file """
		try:
			filesystem.makedir(filesystem.split(filename)[0], True)
			with open(filename, "wb") as file:
				file.write(struct.pack("B"*1440, *HourlyCounter.counter.pulses))
			HourlyCounter.counter.last_save = time.time()
		except Exception as err:
			logger.exception(err)

	@staticmethod
	def load(filename, pulses=None):
		""" Load pulses file """
		result = [0]*1440
		try:
			with open(filename, "rb") as file:
				load_pulses = struct.unpack("B"*1440, file.read())
				index = 0
				if pulses is None:
					result = list(load_pulses)
				else:
					result = pulses
					for pulse in load_pulses:
						result[index] += pulse
						index += 1
		except Exception as err:
			logger.exception(err)
		return result

	@staticmethod
	def get_power():
		""" Return power instantaneous """
		return HourlyCounter.counter.watt_hour

	def simulate(self, pulses):
		""" Simulates the flashing led on the electric meter """
		self.pulse_sensor.simulate(pulses)

	@staticmethod
	async def task(gpio):
		""" Task to count wh from the electric meter """
		HourlyCounter.counter = HourlyCounter(gpio)
		await tasking.task_monitoring(HourlyCounter.counter.manage)

	@staticmethod
	def get_datas(selected_date):
		""" Return the pulse filename according to the selected date """
		if type(selected_date) == type(b""):
			selected_date = date.html_to_date(selected_date)

		if selected_date is None or HourlyCounter.is_same_day(selected_date, time.time()):
			result = HourlyCounter.counter.pulses
		else:
			result = HourlyCounter.load(HourlyCounter.get_filename(selected_date))
		return result

	@staticmethod
	async def pulse_simulator():
		""" Simulates the flashing led on the electric meter """
		import random
		while True:
			HourlyCounter.counter.simulate(random.randint(1, 4))
			await uasyncio.sleep(random.randint(1, 5))

class DailyCounter:
	""" Daily counter of wh consumed """
	@staticmethod
	def get_filename(selected_date=None):
		""" Return the filename according to selected date """
		global PULSE_DIRECTORY, PULSE_DAILY
		if selected_date is None:
			selected_date = time.time()
		year,month = date.local_time(selected_date)[:2]
		return "%s/%04d-%02d/%04d-%02d%s"%(PULSE_DIRECTORY, year, month, year, month, PULSE_DAILY)

	@staticmethod
	def get_datas(selected_date):
		""" Return the pulse filename according to the month selected """
		result = []
		filename = DailyCounter.get_filename(selected_date)
		slot_pulses = DailyCounter.load(filename)
		for time_slot, days in slot_pulses.items():
			result.append({"time_slot":time_slot,"days":days})
		return result

	@staticmethod
	def load(filename):
		""" Load daily file """
		result = {}
		try:
			with open(filename, "rb") as file:
				while True:
					data = file.read(2)
					if len(data) == 0:
						break
					start = struct.unpack("H", data)[0]*60
					end   = struct.unpack("H", file.read(2))[0]*60
					days = struct.unpack("H"*31, file.read(2*31))
					result[(start,end)] = days
		except OSError:
			pass
		except Exception as err:
			logger.exception(err)
		return result

	@staticmethod
	def save(filename, slot_pulses):
		""" Save daily file """
		try:
			with open(filename, "wb") as file:
				for time_slot, days in slot_pulses.items():
					start, end = time_slot
					file.write(struct.pack("HH", start//60, end//60))
					file.write(struct.pack("H"*len(days), *days))
		except OSError:
			pass
		except Exception as err:
			logger.exception(err)

	@staticmethod
	async def update(filenames, daily_to_update):
		""" Update daily files """
		for key, daily_filename in daily_to_update.items():
			year, month = key
			print("Update %s\n  "%daily_filename, end="")
			hourly_searched = "%s/%s-%s/%s-%s*%s"%(PULSE_DIRECTORY, year, month, year, month, PULSE_HOURLY)
			slot_pulses = TimeSlotsConfig.create_empty_slot(31)
			for hourly_filename in filenames:
				if fnmatch.fnmatch(hourly_filename, hourly_searched):
					name = filesystem.splitext(filesystem.split(hourly_filename)[1])[0]
					day = int(name.split("-")[-1])
					print("%d "%day, end="")
					hourly_pulses = HourlyCounter.load(hourly_filename)
					second = 0
					for start, end in slot_pulses.keys():
						second = 0
						for pulses in hourly_pulses:
							if start <= second <= end:
								slot_pulses[(start,end)][day-1] += pulses
							second += 60
				else:
					pass
				await uasyncio.sleep_ms(2)
			print("")
			await uasyncio.sleep_ms(2)
			DailyCounter.save(daily_filename, slot_pulses)

class MonthlyCounter:
	""" Monthly counter of wh consumed """
	last_update = [0]
	next_update = [0]
	force = [True]

	@staticmethod
	async def update(filenames, monthly_to_update):
		""" Update monthly files """
		for year, monthly_filename in monthly_to_update.items():
			print("Update %s\n  "%monthly_filename, end="")
			daily_searched = "%s/%s-*/%s-*%s"%(PULSE_DIRECTORY, year, year, PULSE_DAILY)
			slot_pulses = TimeSlotsConfig.create_empty_slot(12)
			for daily_filename in filenames:
				if fnmatch.fnmatch(daily_filename, daily_searched):
					name = filesystem.splitext(filesystem.split(daily_filename)[1])[0]
					month = int(name.split("-")[-1])
					print("%d "%month, end="")
					daily_slot_pulses = DailyCounter.load(daily_filename)
					for time_slot, days in daily_slot_pulses.items():
						for day in days:
							slot_pulses[time_slot][month-1] = slot_pulses[time_slot][month-1]+day
				await uasyncio.sleep_ms(2)
			print("")
			MonthlyCounter.save(monthly_filename, slot_pulses)
			await uasyncio.sleep_ms(2)

	@staticmethod
	def save(filename, slot_pulses):
		try:
			with open(filename, "wb") as file:
				for time_slot, months in slot_pulses.items():
					start, end = time_slot
					file.write(struct.pack("HH", start//60, end//60))
					file.write(struct.pack("I"*len(months), *months))
		except Exception as err:
			logger.exception(err)

	@staticmethod
	def load(filename):
		""" Load daily file content """
		result = {}
		try:
			with open(filename, "rb") as file:
				while True:
					data = file.read(2)
					if len(data) == 0:
						break
					start = struct.unpack("H", data)[0]*60
					end   = struct.unpack("H", file.read(2))[0]*60
					months = struct.unpack("I"*12, file.read(4*12))
					result[(start,end)] = months
		except Exception as err:
			logger.exception(err)
		return result

	@staticmethod
	async def get_updates():
		""" Build the list of daily and monthly file to update """
		global PULSE_DIRECTORY, PULSE_MONTHLY, PULSE_DAILY
		force = MonthlyCounter.force[0]
		_, filenames = await filesystem.ascandir(PULSE_DIRECTORY, "*", True)
		filenames.sort()
		daily_to_update = {}
		monthly_to_update = {}
		for filename in filenames:
			if fnmatch.fnmatch(filename, "*"+PULSE_HOURLY):
				name = filesystem.splitext(filesystem.split(filename)[1])[0]
				year, month, day = name.split("-")
				daily   = "%s/%s-%s/%s-%s%s"%(PULSE_DIRECTORY, year, month, year, month, PULSE_DAILY)
				monthly = "%s/%s%s"%(PULSE_DIRECTORY, year, PULSE_MONTHLY)
				update = False
				if daily not in daily_to_update:
					if filesystem.exists(daily):
						daily_date  = filesystem.fileinfo(daily)[8]
						hourly_date = filesystem.fileinfo(filename)[8]
						if hourly_date > daily_date or force:
							update = True
					else:
						update = True
				if update:
					daily_to_update[(year, month)] = daily
					monthly_to_update[year] = monthly
			await uasyncio.sleep_ms(2)
		MonthlyCounter.force[0] = False
		return daily_to_update, monthly_to_update, filenames

	@staticmethod
	def get_filename(selected_date=None):
		""" Return the filename according to day """
		global PULSE_DIRECTORY, PULSE_MONTHLY
		if selected_date is None:
			selected_date = time.time()
		year = date.local_time(selected_date)[0]
		return "%s/%04d%s"%(PULSE_DIRECTORY, year, PULSE_MONTHLY)

	@staticmethod
	def get_datas(selected_date):
		""" Return the pulse filename according to the month selected """
		result = []
		slot_pulses = MonthlyCounter.load(MonthlyCounter.get_filename(selected_date))
		for time_slot, months in slot_pulses.items():
			result.append({"time_slot":time_slot,"months":months})
		return result

	@staticmethod
	async def refresh():
		""" Refresh the counters """
		if MonthlyCounter.last_update[0] + 599 < time.time():
			MonthlyCounter.next_update[0] = 0

	@staticmethod
	async def manage():
		""" Rebuild all month files if necessary """
		while True:
			if MonthlyCounter.next_update[0] <= 0:
				break
			MonthlyCounter.next_update[0] -= 1
			await uasyncio.sleep(1)

		daily_to_update, monthly_to_update, filenames = await MonthlyCounter().get_updates()
		await DailyCounter.update  (filenames, daily_to_update)
		await MonthlyCounter.update(filenames, monthly_to_update)
		MonthlyCounter.next_update[0] = 28793
		MonthlyCounter.last_update[0] = time.time()
		return True

	@staticmethod
	async def task():
		""" Task to count wh from the electric meter """
		await tasking.task_monitoring(MonthlyCounter.manage)

class Consumption:
	""" Stores the consumption of a time slot """
	def __init__(self, name, currency):
		""" Constructor """
		self.name = strings.tostrings(name)
		self.cost = 0.
		self.pulses = 0
		self.currency = strings.tostrings(currency)

	def add(self, pulses, price):
		""" Add wh pulses with its price """
		cumul_pulses = 0
		for pulse in pulses:
			cumul_pulses += pulse

		self.cost += cumul_pulses*price/1000
		self.pulses += cumul_pulses

	def to_string(self):
		""" Convert to string """
		return "%s : %.2f %s (%.3f kWh)"%(self.name, self.cost, strings.tostrings(self.currency), self.pulses/1000)

class Cost:
	""" Abstract class to compute the cost """
	def get_rates(self, selected_date):
		""" Get the rate according to the selected date """
		prices = TimeSlotsConfig.get_cost(selected_date)
		consumptions = {}
		for price in prices:
			consumptions[price[b"rate"]] = Consumption(price[b"rate"], price[b"currency"])
		return prices, consumptions

	def compute(self, selected_date):
		""" Compute cost """
		return {}

	def get_message(self, title, selected_date):
		""" Get result message """
		consumptions = self.compute(selected_date)
		result = " - " + strings.tostrings(title) + " :\n"
		for consumption in consumptions.values():
			result += "   %s\n"%consumption.to_string()
		return result

class HourlyCost(Cost):
	""" Hourly cost calculation """
	def compute(self, selected_date):
		""" Compute cost """
		prices, consumptions = self.get_rates(selected_date)
		pulses = HourlyCounter.load(HourlyCounter.get_filename(selected_date))
		second = 0
		for pulse in pulses:
			for price in prices:
				if price[b"start_time"] <= second <= price[b"end_time"]:
					consumptions[price[b"rate"]].add([pulse], price[b"price"])
					break
			second += 60
		return consumptions

class DailyCost(Cost):
	""" Daily cost calculation """
	def compute(self, selected_date):
		""" Compute cost """
		slot_pulses = DailyCounter.load(DailyCounter.get_filename(selected_date))
		prices,consumptions = self.get_rates(selected_date)
		for slot_time, pulses in slot_pulses.items():
			for price in prices:
				start, end = slot_time
				if price[b"start_time"] == start and price[b"end_time"] == end:
					consumptions[price[b"rate"]].add(pulses, price[b"price"])
					break
		return consumptions

def daily_notifier():
	""" Get electricmeter daily notification """
	selected_date = time.time() - 86400
	message = "\n"
	cost = HourlyCost()
	message += cost.get_message(em_lang.item_day, selected_date)
	cost = DailyCost()
	message += cost.get_message(em_lang.item_month, selected_date)
	message += " - Lan Ip : %s\n"%wifi.Station.get_info()[0]
	message += " - Wan Ip : %s\n"%Server.context.wan_ip
	message += " - Uptime : %s\n"%strings.tostrings(info.uptime())
	return message

def create_electric_meter(loop, gpio=21):
	""" Create user task """
	Server.set_daily_notifier(daily_notifier)
	loop.create_task(HourlyCounter.task(gpio))
	loop.create_task(MonthlyCounter.task())
	if filesystem.ismicropython() is False:
		loop.create_task(HourlyCounter.pulse_simulator())
