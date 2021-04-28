# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Manage the motion detection history file """
import uos
import re
import uasyncio
from tools import useful
import json
import server

class Historic:
	""" Manage the motion detection history file """
	detectionCount    = [0]
	detectionPrevious = [-1]
	motionInProgress  = [False]

	@staticmethod
	async def build(mountpoint, directories):
		""" Parse the all motions files to build historic """
		result = []
		count = 0
		try:
			# For all directories
			for directory in directories:
				path = mountpoint + "/" + directory

				# Open directory
				for fileinfo in uos.ilistdir(path):
					filename = fileinfo[0]
					typ = fileinfo[1]
					# If file detected
					if typ & 0xF000 != 0x4000:
						# If file is json type
						if re.match(".*\.json", filename):
							try:
								# Parse json file
								file = open(path + "/" + filename, "rb")
								content = json.load(file)
								file.close()
								content["image"] = path + "/" + content["image"]
								# Add json file to the historic
								result.append([content["date"], content])
							except Exception as err:
								print(useful.exception(err))
					count += 1
					if count > 10:
						count = 0
						await sleep_ms(5)
		except Exception as err:
			print(useful.exception(err))
		result.sort()
		result.reverse()
		return result

	@staticmethod
	async def extractHistoric(directory):
		""" Extract motion historic """
		# If historic must be refreshed
		if Historic.detectionCount[0] != Historic.detectionPrevious[0]:
			try:
				Historic.detectionPrevious[0] = Historic.detectionCount[0]

				useful.log("Start build historic")
				# Scan sd card and get more recent directories
				directories = await Historic.scanDirectories(useful.SdCard.getMountpoint(), 50, False)

				# Build historic file
				files = await Historic.build(useful.SdCard.getMountpoint(), directories)
    
				# Save historic file
				file = open(directory +"/historic.json", "w")
				json.dump(files, file)
				file.close()
				useful.log("End   build historic")

			except Exception as err:
				print(useful.exception(err))

	@staticmethod
	async def scanDirectories(mountpoint, quantity=10, older=True):
		""" Get the list of older or newer directories in the sd card """
		directories = []
		count = 0
		# Parse all directories in sdcard
		for fileinfo in uos.ilistdir(useful.SdCard.getMountpoint()):
			filename = fileinfo[0]
			typ = fileinfo[1]
			# If directory found
			if typ & 0xF000 == 0x4000:
				# If motion directory recognized
				if re.match("\d\d\d\d-\d\d-\d\d \d\d-\d\d-\d\d", filename):
					# Add directory to the list
					directories.append(filename)
					if len(directories) > (quantity + 10):
						directories.sort()
						if older == False:
							directories.reverse()
						directories = directories[:quantity]
			count += 1
			if count > 10:
				count = 0
				await sleep_ms(5)

		directories.sort()
		if older == False:
			directories.reverse()
		directories = directories[:quantity]
		return directories

	@staticmethod
	def setMotionState(state):
		""" Indicates if motion is actually in detection """
		Historic.motionInProgress[0] = state
  
	@staticmethod
	def setDetection():
		""" Indicates that motion detected """
		Historic.detectionCount[0] += 1

	@staticmethod
	async def removeFiles(directory, simulate=False):
		""" Remove all files in the directory """
		import shell
		notEmpty = False
		# Parse all directories in sdcard
		for fileinfo in uos.ilistdir(directory):
			filename = fileinfo[0]
			typ      = fileinfo[1]
			# If file found
			if typ & 0xF000 != 0x4000:
				shell.rmfile(directory + "/" + filename, simulate=simulate)
			else:
				await Historic.removeFiles(directory + "/" + filename)
				notEmpty = True
			await sleep_ms(5)
		
		if notEmpty:
			shell.rm(directory, recursive=True, simulate=simulate)
		else:
			shell.rmdir(directory, recursive=True, simulate=simulate)

	@staticmethod
	async def removeOlder(directory):
		""" Remove older files to make space """
		# If not enough space available on sdcard
		if useful.SdCard.getFreeSize() * 10000// useful.SdCard.getMaxSize() <= 5:
			olders = await Historic.scanDirectories(useful.SdCard.getMountpoint())
			for directory in olders:
				await Historic.removeFiles(useful.SdCard.getMountpoint()+ "/"+ directory)

	@staticmethod
	async def periodicTask():
		""" Execute periodic traitment """
		while 1:
			await sleep_ms(60000)
			await server.waitResume()
			if Historic.motionInProgress[0] == False:
				if useful.SdCard.isMounted():
					await Historic.extractHistoric(useful.SdCard.getMountpoint())
					await Historic.removeOlder(useful.SdCard.getMountpoint())


async def sleep_ms(duration):
	""" Multiplatform sleep_ms """
	await uasyncio.sleep_ms(duration)


	





