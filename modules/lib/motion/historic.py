# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Manage the motion detection history file """
import re
import json
import uasyncio
import uos
from tools import useful, sdcard, tasking

MAX_DISPLAYED = 100
MAX_REMOVED   = 100

class Historic:
	""" Manage the motion detection history file """
	motion_in_progress  = [False]
	historic = []
	first_extract = [False]
	lock = uasyncio.Lock()

	@staticmethod
	async def acquire():
		""" Lock historic """
		await Historic.lock.acquire()

	@staticmethod
	async def release():
		""" Release historic """
		Historic.lock.release()

	@staticmethod
	async def locked():
		""" Indicates if historic is locked """
		return Historic.lock.locked()

	@staticmethod
	async def get_root():
		""" Get the root path of sdcard and mount it """
		if sdcard.SdCard.mount():
			return sdcard.SdCard.get_mountpoint()
		return None

	@staticmethod
	async def add_motion(path, name, image, info):
		""" Add motion detection in the historic """
		root = await Historic.get_root()
		result = False
		if root:
			try:
				await Historic.acquire()
				path = useful.tostrings(path)
				name = useful.tostrings(name)
				item = Historic.create_item(root + "/" + path + "/" + name +".json", info)
				res1 = sdcard.SdCard.save(path, name + ".jpg" , image)
				res2 = sdcard.SdCard.save(path, name + ".json", json.dumps(item))
				Historic.add_item(item)
				result = res1 and res2
			except Exception as err:
				useful.syslog(err)
			finally:
				await Historic.release()
		return result

	@staticmethod
	def create_item(filename, info):
		""" Create historic item """
		name = useful.splitext(filename)[0] + ".jpg"
		result = None
		if "geometry" in info:
			# Add json file to the historic
			result = [name, info["geometry"]["width"],info["geometry"]["height"], info["diff"]["diffs"], info["diff"]["squarex"], info["diff"]["squarey"]]
		return result

	@staticmethod
	def add_item(item):
		""" Add item in the historic """
		if item is not None:
			if not useful.ismicropython():
				# Remove the "/" before filename
				item [0] = item[0][1:]
			# Add json file to the historic
			Historic.historic.insert(0,item)

	@staticmethod
	async def build(motions):
		""" Parse the all motions files to build historic """
		root = await Historic.get_root()
		if root:
			count = 0
			try:
				await Historic.acquire()
				Historic.historic.clear()

				# For all motions
				for motion in motions:
					path = root + "/" + motion

					try:
						# Parse json file
						file = None
						file = open(motion, "rb")
						Historic.add_item(json.load(file))
					except Exception as err:
						useful.syslog(err)
					finally:
						if file:
							file.close()
					await uasyncio.sleep_ms(3)
			except Exception as err:
				useful.syslog(err)
			finally:
				await Historic.release()

	@staticmethod
	async def get_json():
		""" Read the historic from disk """
		root = await Historic.get_root()
		result = b""
		if root:
			try:
				await Historic.acquire()
				Historic.historic.sort()
				Historic.historic.reverse()
				while len(Historic.historic) > MAX_DISPLAYED:
					del Historic.historic[-1]
				result = useful.tobytes(json.dumps(Historic.historic))
			except Exception as err:
				useful.syslog(err)
			finally:
				await Historic.release()
		return result

	@staticmethod
	async def extract():
		""" Extract motion historic """
		# If this is the fisrt update (parse all directory)
		if  Historic.first_extract[0] is False:
			Historic.first_extract[0] = True
			try:
				useful.syslog("Start historic creation")
				# Scan sd card and get more recent motions
				motions = await Historic.scan_directories(MAX_DISPLAYED, False)

				# Build historic file
				files = await Historic.build(motions)
				useful.syslog("End   historic creation")
			except Exception as err:
				useful.syslog(err)

	@staticmethod
	async def scan_dir(path, pattern, older=True, directory=True):
		""" Scan directory """
		result = []
		count = 0
		for fileinfo in uos.ilistdir(path):
			name = fileinfo[0]
			typ  = fileinfo[1]
			if directory:
				if typ & 0xF000 == 0x4000:
					if re.match(pattern, name):
						result.append(name)
			else:
				if typ & 0xF000 != 0x4000:
					if re.match(pattern, name):
						result.append(name)
			count += 1
			if count > 10:
				count = 0
				await uasyncio.sleep_ms(5)
		result.sort()
		if older is False:
			result.reverse()
		return result

	@staticmethod
	async def scan_directories(quantity=10, older=True):
		""" Get the list of older or older directories in the sd card """
		motions = []
		root = await Historic.get_root()
		if root:
			try:
				await Historic.acquire()
				years = await Historic.scan_dir(root, r"\d\d\d\d", older)
				for year in years:
					pathYear = root + "/" + year
					months = await Historic.scan_dir(pathYear, r"\d\d", older)
					for month in months:
						pathMonth = pathYear + "/" + month
						days = await Historic.scan_dir(pathMonth, r"\d\d", older)
						for day in days:
							pathDay = pathMonth + "/" + day
							hours = await Historic.scan_dir(pathDay, r"\d\dh\d\d", older)
							for hour in hours:
								pathHour = pathDay + "/" + hour
								if older:
									extension = "jpg"
								else:
									extension = "json"
								detections = await Historic.scan_dir(pathHour, r"\d\d.*\."+extension, older, directory=False)
								for detection in detections:
									motions.append(pathHour + "/" + detection)
								if len(motions) > quantity:
									motions.sort()
									if older is False:
										motions.reverse()
									return motions
				motions.sort()
				if older is False:
					motions.reverse()
			except Exception as err:
				useful.syslog(err)
			finally:
				await Historic.release()
		return motions

	@staticmethod
	def set_motion_state(state):
		""" Indicates if motion is actually in detection """
		Historic.motion_in_progress[0] = state

	@staticmethod
	async def remove_files(directory, simulate=False):
		""" Remove all files in the directory """
		import shell
		notEmpty = False
		force = True
		if useful.exists(directory):
			# Parse all directories in sdcard
			for fileinfo in uos.ilistdir(directory):
				filename = fileinfo[0]
				typ      = fileinfo[1]
				print(filename)
				# If file found
				if typ & 0xF000 != 0x4000:
					shell.rmfile(directory + "/" + filename, simulate=simulate, force=force)
				else:
					await Historic.remove_files(directory + "/" + filename)
					notEmpty = True

			if notEmpty:
				shell.rm(directory, recursive=True, simulate=simulate, force=force)
			else:
				shell.rmdir(directory, recursive=True, simulate=simulate, force=force)
		else:
			print("Directory not existing '%s'"%directory)

	@staticmethod
	async def remove_older(force=False):
		""" Remove older files to make space """
		root = await Historic.get_root()
		if root:
			# If not enough space available on sdcard
			if (sdcard.SdCard.get_free_size() * 10000// sdcard.SdCard.get_max_size() <= 5) or force:
				useful.syslog("Start cleanup sd card")
				olders = await Historic.scan_directories(MAX_REMOVED, True)
				previous = ""
				for motion in olders:
					try:
						await Historic.acquire()
						directory = useful.split(motion)[0]
						if previous != directory:
							await Historic.remove_files(directory)
							previous = directory
					except Exception as err:
						useful.syslog(err)
					finally:
						await Historic.release()
				useful.syslog("End cleanup sd card")

	@staticmethod
	async def periodic():
		""" Internal periodic task """
		from server.server import Server
		if useful.ismicropython():
			await Server.wait_resume(307)
		else:
			await Server.wait_resume(7)
		if Historic.motion_in_progress[0] is False:
			if sdcard.SdCard.is_mounted():
				await Historic.extract()
				await Historic.remove_older()
			else:
				await Historic.get_root()
		return True

	@staticmethod
	async def periodic_task():
		""" Execute periodic traitment """
		await tasking.task_monitoring(Historic.periodic)

	@staticmethod
	async def test():
		""" Test historic """
		await Historic.extract()
		await Historic.remove_older(True)
