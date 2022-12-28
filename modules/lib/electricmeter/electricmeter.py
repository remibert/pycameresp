""" Task to count wh from the electric meter """
import struct
import time
import collections
import uasyncio
import machine
from electricmeter.config   import TimeSlotsConfig
from tools import filesystem, date, fnmatch, logger, tasking
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
		self.pulses = self.load(self.day)
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
			if self.is_same_day(day, self.day) is False:
				# Save day counter
				self.save(self.day)

				# Clear day pulses counter
				self.day_pulses_counter = 0

				# Load new day if existing or clear counter (manage day light saving)
				self.pulses = self.load(day)
				self.day = day

		# Each ten minutes
		if time.time() > (self.last_save + 67):
			# Save pulses file
			self.save(self.day)

		# print("%s %.1f wh pulses=%d"%(date.date_to_string(), self.watt_hour, self.day_pulses_counter))
		return True

	def is_same_day(self, day1, day2):
		""" Indicates if the day 1 is equal to day 2"""
		if day1//86400 == day2//86400 or day1 is None or day2 is None:
			return True
		else:
			return False

	def get_filename(self, day=None):
		""" Return the filename according to day """
		global PULSE_DIRECTORY, PULSE_HOURLY
		if day is None:
			day = time.time()
		year,month,day = date.local_time(day)[:3]
		return "%s/%04d-%02d/%04d-%02d-%02d%s"%(PULSE_DIRECTORY, year, month, year, month, day, PULSE_HOURLY)

	def save(self, day):
		""" Save pulses file """
		filename  = self.get_filename(day)
		# print("Save day %s"%filename)
		filesystem.makedir(filesystem.split(filename)[0], True)
		with open(filename, "wb") as file:
			file.write(struct.pack("B"*1440, *self.pulses))
		self.last_save = time.time()

	def load(self, day=None, pulses=None):
		""" Load pulses file """
		if pulses is None:
			pulses = [0]*1440
		try:
			filename = self.get_filename(day)
			# print("Load day %s"%filename)
			with open(filename, "rb") as file:
				content = file.read()
				index = 0
				for byte in content:
					pulses[index] += byte
					index += 1
		except OSError:
			pass
		return pulses

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
	def get_datas(day):
		""" Return the pulse filename according to the day selected """
		if type(day) == type(b""):
			day = date.html_to_date(day)

		if day is None or HourlyCounter.counter.is_same_day(day, time.time()):
			result = HourlyCounter.counter.pulses
		else:
			result = HourlyCounter.counter.load(day)
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
	def get_filename(day=None):
		""" Return the filename according to day """
		global PULSE_DIRECTORY, PULSE_DAILY
		if day is None:
			day = time.time()
		year,month,day = date.local_time(day)[:3]
		return "%s/%04d-%02d/%04d-%02d%s"%(PULSE_DIRECTORY, year, month, year, month, PULSE_DAILY)

	@staticmethod
	def get_datas(month):
		""" Return the pulse filename according to the month selected """
		result = []
		try:
			filename = DailyCounter.get_filename(month)
			# print("Load month %s"%filename)
			with open(filename, "rb") as file:
				while True:
					data = file.read(2)
					if len(data) == 0:
						break
					start = struct.unpack("H", data)[0]*60
					end   = struct.unpack("H", file.read(2))[0]*60
					days = struct.unpack("H"*31, file.read(2*31))
					result.append({"time_slot":(start,end),"days":days})
		except OSError:
			pass
		except Exception as err:
			logger.exception(err)
		return result

	@staticmethod
	def create_empty():
		""" Create empty daily data """
		time_slots = TimeSlotsConfig()
		time_slots.load()

		slots = []
		index = 0
		while True:
			slot = time_slots.get(index)
			if slot is None:
				break
			slots.append((slot[b"start_time"]//60, slot[b"end_time"]//60))
			index += 1
		if len(slots) == 0:
			slots.append((0,1439))

		slot_pulses = {}
		for start, end in slots:
			slot_pulses[(start,end)] = [0]*31
		return slots, slot_pulses

	@staticmethod
	async def update(filenames, daily_to_update):
		""" Update daily files """
		for key, daily_filename in daily_to_update.items():
			year, month = key
			print("Update %s\n  "%daily_filename, end="")
			hourly_searched = "%s/%s-%s/%s-%s*%s"%(PULSE_DIRECTORY, year, month, year, month, PULSE_HOURLY)
			slots, slot_pulses = DailyCounter.create_empty()
			for hourly_filename in filenames:
				if fnmatch.fnmatch(hourly_filename, hourly_searched):
					name = filesystem.splitext(filesystem.split(hourly_filename)[1])[0]
					day = int(name.split("-")[-1])
					print("%d "%day, end="")
					with open(hourly_filename, "rb") as file:
						content = file.read()
						hour = 0
						for start, end in slots:
							hour = 0
							for byte in content:
								if start <= hour <= end:
									slot_pulses[(start,end)][day-1] += byte
								hour += 1
				else:
					pass
			print("")
			await uasyncio.sleep_ms(3)
			with open(daily_filename, "wb") as file:
				for start, end in slots:
					file.write(struct.pack("HH", start, end))
					file.write(struct.pack("H"*len(slot_pulses[(start,end)]), *slot_pulses[(start,end)]))

class MonthlyCounter:
	""" Monthly counter of wh consumed """
	last_update = [0]
	next_update = [0]
	force = [True]
	@staticmethod
	def create_empty():
		""" Create empty monthly datas """
		time_slots = TimeSlotsConfig()
		time_slots.load()

		slots = []
		index = 0
		while True:
			slot = time_slots.get(index)
			if slot is None:
				break
			slots.append((slot[b"start_time"]//60, slot[b"end_time"]//60))
			index += 1
		if len(slots) == 0:
			slots.append((0,1439))

		slot_pulses = {}
		for start, end in slots:
			slot_pulses[(start,end)] = [0]*12
		return slots, slot_pulses

	@staticmethod
	async def update(filenames, monthly_to_update):
		""" Update monthly files """
		for year, monthly_filename in monthly_to_update.items():
			print("Update %s\n  "%monthly_filename, end="")
			daily_searched = "%s/%s-*/%s-*%s"%(PULSE_DIRECTORY, year, year, PULSE_DAILY)
			slots, slot_pulses = MonthlyCounter.create_empty()
			for daily_filename in filenames:
				if fnmatch.fnmatch(daily_filename, daily_searched):
					name = filesystem.splitext(filesystem.split(daily_filename)[1])[0]
					month = int(name.split("-")[-1])
					print("%d "%month, end="")
					with open(daily_filename, "rb") as file:
						while True:
							data = file.read(2)
							if len(data) == 0:
								break
							start = struct.unpack("H", data)[0]
							end   = struct.unpack("H", file.read(2))[0]
							days = struct.unpack("H"*31, file.read(2*31))
							for day in days:
								if (start,end) in slot_pulses.keys():
									try:
										slot_pulses[(start,end)][month-1] = slot_pulses[(start,end)][month-1]+day
									except Exception as err:
										pass
								else:
									pass
			print("")
			with open(monthly_filename, "wb") as file:
				for start, end in slots:
					file.write(struct.pack("HH", start, end))
					file.write(struct.pack("I"*len(slot_pulses[(start,end)]), *slot_pulses[(start,end)]))

	@staticmethod
	async def get_updates():
		""" Build the list of daily and monthly file to update """
		global PULSE_DIRECTORY, PULSE_MONTHLY, PULSE_DAILY
		force = MonthlyCounter.force[0]
		directories, filenames = filesystem.scandir(PULSE_DIRECTORY, "*", True)
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
		MonthlyCounter.force[0] = False
		return daily_to_update, monthly_to_update, filenames

	@staticmethod
	def get_filename(day=None):
		""" Return the filename according to day """
		global PULSE_DIRECTORY, PULSE_MONTHLY
		if day is None:
			day = time.time()
		year = date.local_time(day)[0]
		return "%s/%04d%s"%(PULSE_DIRECTORY, year, PULSE_MONTHLY)

	@staticmethod
	def get_datas(month):
		""" Return the pulse filename according to the month selected """
		result = []
		try:
			filename = MonthlyCounter.get_filename(month)
			# print("Load month %s"%filename)
			with open(filename, "rb") as file:
				while True:
					data = file.read(2)
					if len(data) == 0:
						break
					start = struct.unpack("H", data)[0]*60
					end   = struct.unpack("H", file.read(2))[0]*60
					
					months = struct.unpack("I"*12, file.read(4*12))
					result.append({"time_slot":(start,end),"months":months})
		except OSError:
			pass
		except Exception as err:
			logger.exception(err)
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

def create_electric_meter(loop, gpio=21):
	""" Create user task """
	loop.create_task(HourlyCounter.task(gpio))
	loop.create_task(MonthlyCounter.task())
	if filesystem.ismicropython() is False:
		loop.create_task(HourlyCounter.pulse_simulator())
