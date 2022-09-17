# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Manage the motion detection history file """
import re
import json
import uasyncio
import uos
from tools import logger,sdcard,tasking,filesystem,strings,info

MAX_DAYS_DISPLAYED = 14
MAX_DAYS_REMOVED   = 14
MAX_MOTIONS        = 300

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
	def get_root():
		""" Get the root path of sdcard and mount it """
		if sdcard.SdCard.mount():
			return sdcard.SdCard.get_mountpoint()
		return None

	@staticmethod
	async def add_motion(path, name, image, motion_info):
		""" Add motion detection in the historic """
		root = Historic.get_root()
		result = False
		if root:
			try:
				await Historic.acquire()
				path = strings.tostrings(path)
				name = strings.tostrings(name)
				item = Historic.create_item(root + "/" + path + "/" + name +".json", motion_info)
				res1 = sdcard.SdCard.save(path, name + ".jpg" , image)
				res2 = sdcard.SdCard.save(path, name + ".json", json.dumps(item, separators=(',', ':')))
				Historic.add_item(item)
				result = res1 and res2
			except Exception as err:
				logger.syslog(err)
			finally:
				await Historic.release()
		return result

	@staticmethod
	def create_item(filename, motion_info):
		""" Create historic item """
		name = filesystem.splitext(filename)[0] + ".jpg"
		result = None
		if "geometry" in motion_info:
			# Add json file to the historic
			result = [name, motion_info["geometry"]["width"],motion_info["geometry"]["height"], motion_info["diff"]["diffs"], motion_info["diff"]["squarex"], motion_info["diff"]["squarey"]]
		return result

	@staticmethod
	def add_item(item):
		""" Add item in the historic """
		if item is not None:
			if not filesystem.ismicropython():
				# Remove the "/" before filename
				item [0] = item [0].lstrip("/")

			# If the differences are in an old format
			if type(item[3]) == type(""):
				diffs = []
				diffVal = 0
				i = 0
				for diff in item[3]:
					if diff == "#":
						diffVal |= 1

					if (i %32 == 31):
						diffs.append(diffVal)
						diffVal = 0
					else:
						diffVal <<= 1
					i += 1
				diffMax = len(item[3])
				diffVal <<= (31 - (diffMax%32))
				diffs.append(diffVal)
				item[3] = diffs

			# Add json file to the historic
			Historic.historic.insert(0,item)

	@staticmethod
	async def build(motions):
		""" Parse the all motions files to build historic """
		root = Historic.get_root()
		if root:
			try:
				await Historic.acquire()
				Historic.historic.clear()
				last_day = ""
				# For all motions
				for motion in motions:
					try:
						# Parse json file
						file = None
						file = open(motion, "rb")
						motion_item = json.load(file)
						filename = motion_item[0]
						if not filesystem.ismicropython():
							filename = filename.lstrip("/")
						if filesystem.exists(filename):
							Historic.add_item(motion_item)
						if last_day != motion_item[0][4:14]:
							last_day = motion_item[0][4:14]
							print("Build historic day %s"%last_day)
					except OSError as err:
						logger.syslog(err)
						# If sd card not responding properly
						if err.errno == 2:
							info.increase_issues_counter()
					except Exception as err:
						logger.syslog(err)
					finally:
						if file:
							file.close()
					await uasyncio.sleep_ms(2)
			except Exception as err:
				logger.syslog(err)
			finally:
				await Historic.release()

	@staticmethod
	async def get_json():
		""" Read the historic from disk """
		root = Historic.get_root()
		result = b"[]"
		if root:
			try:
				await Historic.acquire()
				Historic.historic.sort()
				Historic.historic.reverse()
				while len(Historic.historic) > MAX_MOTIONS:
					del Historic.historic[-1]
				result = strings.tobytes(json.dumps(Historic.historic, separators=(',', ':')))
			except Exception as err:
				logger.syslog(err)
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
				logger.syslog("Start historic creation")
				# Scan sd card and get more recent motions
				motions, lastdays = await Historic.scan_directories(MAX_DAYS_DISPLAYED, False)

				# Build historic file
				files = await Historic.build(motions)
				logger.syslog("Historic contains :")
				for day in lastdays:
					logger.syslog("   %s"%day)
				logger.syslog("End   historic creation")
				logger.syslog(strings.tostrings(info.flashinfo(mountpoint=sdcard.SdCard.get_mountpoint())))
			except Exception as err:
				logger.syslog(err)

	@staticmethod
	async def scan_dir(path, pattern, older=True, directory=True):
		""" Scan directory """
		result = []
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
		await uasyncio.sleep_ms(3)
		result.sort()
		if older is False:
			result.reverse()
		return result

	@staticmethod
	async def scan_directories(max_days=10, older=True):
		""" Get the list of older or older directories in the sd card """
		motions = []
		lastdays = []
		root = Historic.get_root()
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
							print("Scan  historic day %s/%s/%s"%(year, month, day))
							pathDay = pathMonth + "/" + day
							hours = await Historic.scan_dir(pathDay, r"\d\dh\d\d", older)
							lastdays.append("%s/%s/%s"%(year, month, day))

							for hour in hours:
								pathHour = pathDay + "/" + hour
								if older:
									extension = "jpg"
								else:
									extension = "json"
								detections = await Historic.scan_dir(pathHour, r"\d\d.*\."+extension, older, directory=False)
								for detection in detections:
									if len(lastdays) > max_days or len(motions) > MAX_MOTIONS:
										motions.sort()
										if older is False:
											motions.reverse()
										return motions, lastdays
									motions.append(pathHour + "/" + detection)
				motions.sort()
				if older is False:
					motions.reverse()
			except Exception as err:
				logger.syslog(err)
			finally:
				await Historic.release()
		return motions, lastdays

	@staticmethod
	def set_motion_state(state):
		""" Indicates if motion is actually in detection """
		Historic.motion_in_progress[0] = state

	@staticmethod
	async def remove_files(directory, simulate=False, force=False):
		""" Remove all files in the directory """
		import shell
		dir_not_empty = False
		enough_space = False
		force = True
		if filesystem.exists(directory):
			files_to_remove = []
			dirs_to_remove  = []

			# Parse all directories in sdcard (WARNING : TO AVOID CRASH, NEVER DELETE DIRECTORY OR FILE IN ilistdir LOOP)
			for fileinfo in uos.ilistdir(directory):
				filename = fileinfo[0]
				typ      = fileinfo[1]
				# If file found
				if typ & 0xF000 != 0x4000:
					files_to_remove.append(directory + "/" + filename)
				else:
					dirs_to_remove.append(directory + "/" + filename)
				dir_not_empty = True

			for file_to_remove in files_to_remove:
				shell.rmfile(file_to_remove, simulate=simulate, force=force)
				if sdcard.SdCard.is_not_enough_space(low=False) is False:
					enough_space = True
					break

			if enough_space is False:
				for dir_to_remove in dirs_to_remove:
					await Historic.remove_files(dir_to_remove, simulate=simulate, force=force)
				if dir_not_empty:
					shell.rm(directory, recursive=True, simulate=simulate, force=force)
				else:
					shell.rmdir(directory, recursive=True, simulate=simulate, force=force)

	@staticmethod
	async def remove_older(force=False):
		""" Remove older files to make space """
		root = Historic.get_root()
		if root:
			# If not enough space available on sdcard
			if sdcard.SdCard.is_not_enough_space(low=True) or force:
				logger.syslog("Start cleanup historic")
				Historic.first_extract[0] = False
				olders, lastdays = await Historic.scan_directories(MAX_DAYS_REMOVED, True)
				previous = ""
				for motion in olders:
					try:
						await Historic.acquire()
						directory = filesystem.split(motion)[0]
						if previous != directory:
							await Historic.remove_files(directory, simulate=False, force=force)
							previous = directory
					except Exception as err:
						logger.syslog(err)
					finally:
						await Historic.release()
					if sdcard.SdCard.is_not_enough_space(low=False) is False:
						break
				logger.syslog("End cleanup historic : %s"%(strings.tostrings(info.flashinfo(mountpoint=sdcard.SdCard.get_mountpoint()))))

	@staticmethod
	async def periodic():
		""" Internal periodic task """
		from server.server import Server
		if filesystem.ismicropython():
			await Server.wait_resume(127)
		else:
			await Server.wait_resume(3)

		if Historic.motion_in_progress[0] is False:
			if sdcard.SdCard.is_mounted() is False:
				Historic.get_root()
			if sdcard.SdCard.is_mounted():
				await Historic.remove_older()
				await Historic.extract()
		return True

	@staticmethod
	async def periodic_task():
		""" Execute periodic treatment """
		await tasking.task_monitoring(Historic.periodic)

	@staticmethod
	async def test():
		""" Test historic """
		await Historic.extract()
		await Historic.remove_older(True)
