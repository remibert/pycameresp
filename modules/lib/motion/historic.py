# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Manage the motion detection history file """
import uos
import re
import uasyncio
from tools import useful
import json
import server

MAX_DISPLAYED = 100
MAX_REMOVED   = 100

class Historic:
	""" Manage the motion detection history file """
	motionInProgress  = [False]
	historic = []
	firstExtract = [False]
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
	async def getRoot():
		""" Get the root path of sdcard and mount it """
		if useful.SdCard.mount():
			return useful.SdCard.getMountpoint()
		return None

	@staticmethod
	async def addMotion(path, name, image, info, html):
		""" Add motion detection in the historic """
		root = await Historic.getRoot()
		if root:
			try:
				await Historic.acquire()
				useful.makedir(root + "/" + useful.tostrings(path), True)
				filename = path + "/" + name
				jsonInfo = useful.tobytes(json.dumps(info))
				useful.SdCard.save(filename + ".jpg" , image)
				useful.SdCard.save(filename + ".html", html)
				useful.SdCard.save(filename + ".json", jsonInfo)
				Historic.addItem(root + "/" + filename+".json", info)
			except Exception as err:
				print(useful.exception(err))
			finally:
				await Historic.release()

	@staticmethod
	def addItem(filename, info):
		name = useful.splitext(filename)[0] + ".jpg"
		
		shapes = []
		for shape in info["shapes"]:
			shapes.append([shape["size"],shape["x"],shape["y"],shape["width"],shape["height"]])
		# Add json file to the historic
		Historic.historic.insert(0,[name, info["geometry"]["width"],info["geometry"]["height"], shapes])

	@staticmethod
	async def build(motions):
		""" Parse the all motions files to build historic """
		root = await Historic.getRoot()
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
						file = open(motion, "rb")
						Historic.addItem(motion, json.load(file))
					except Exception as err:
						print(useful.exception(err))
					finally:
						file.close()
						count += 1
					if count > 10:
						count = 0
						await sleep_ms(5)
			except Exception as err:
				print(useful.exception(err))
			finally:
				await Historic.release()

	@staticmethod
	async def getJson():
		""" Read the historic from disk """
		root = await Historic.getRoot()
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
				print(useful.exception(err))
			finally:
				await Historic.release()
		return result

	@staticmethod
	async def extract():
		""" Extract motion historic """
		# If this is the fisrt update (parse all directory)
		if  Historic.firstExtract[0] == False:
			Historic.firstExtract[0] = True
			try:
				print("Start historic creation")
				# Scan sd card and get more recent motions
				motions = await Historic.scanDirectories(MAX_DISPLAYED, False)

				# Build historic file
				files = await Historic.build(motions)
				print("End   historic creation")
			except Exception as err:
				print(useful.exception(err))

	@staticmethod
	async def scanDir(path, pattern, older=True, directory=True):
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
				await sleep_ms(5)
		result.sort()
		if older == False:
			result.reverse()
		return result

	@staticmethod
	async def scanDirectories(quantity=10, older=True):
		""" Get the list of older or older directories in the sd card """
		motions = []
		root = await Historic.getRoot()
		if root:
			try:
				await Historic.acquire()
				years = await Historic.scanDir(root, "\d\d\d\d", older)
				for year in years:
					pathYear = root + "/" + year
					months = await Historic.scanDir(pathYear, "\d\d", older)
					for month in months:
						pathMonth = pathYear + "/" + month
						days = await Historic.scanDir(pathMonth, "\d\d", older)
						for day in days:
							pathDay = pathMonth + "/" + day
							hours = await Historic.scanDir(pathDay, "\d\dh\d\d", older)
							for hour in hours:
								pathHour = pathDay + "/" + hour
								if older:
									extension = "jpg"
								else:
									extension = "json"
								detections = await Historic.scanDir(pathHour, "\d\d.*\."+extension, older, directory=False)
								for detection in detections:
									motions.append(pathHour + "/" + detection)
								if len(motions) > quantity:
									motions.sort()
									if older == False:
										motions.reverse()
									return motions
				motions.sort()
				if older == False:
					motions.reverse()
			except Exception as err:
				print(useful.exception(err))
			finally:
				await Historic.release()
		return motions

	@staticmethod
	def setMotionState(state):
		""" Indicates if motion is actually in detection """
		Historic.motionInProgress[0] = state

	@staticmethod
	async def __removeFiles(directory, simulate=False):
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
					await Historic.__removeFiles(directory + "/" + filename)
					notEmpty = True
			
			if notEmpty:
				shell.rm(directory, recursive=True, simulate=simulate, force=force)
			else:
				shell.rmdir(directory, recursive=True, simulate=simulate, force=force)
		else:
			print("Directory not existing '%s'"%directory)

	@staticmethod
	async def removeOlder():
		""" Remove older files to make space """
		root = await Historic.getRoot()
		if root:
			# If not enough space available on sdcard
			if useful.SdCard.getFreeSize() * 10000// useful.SdCard.getMaxSize() <= 5:
				print("Start cleanup sd card")
				olders = await Historic.scanDirectories(MAX_REMOVED, True)
				previous = ""
				for motion in olders:
					try:
						await Historic.acquire()
						directory = useful.split(motion)[0]
						if previous != directory:
							await Historic.__removeFiles(directory)
							previous = directory
					except Exception as err:
						print(useful.exception(err))
					finally:
						await Historic.release()
				print("End cleanup sd card")

	@staticmethod
	async def periodicTask():
		""" Execute periodic traitment """
		while 1:
			await server.waitResume(10)
			if Historic.motionInProgress[0] == False:
				if useful.SdCard.isMounted():
					await Historic.extract()
					await Historic.removeOlder()

async def sleep_ms(duration):
	""" Multiplatform sleep_ms """
	await uasyncio.sleep_ms(duration)







