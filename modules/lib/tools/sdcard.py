# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Sdcard management class """
try:
	import machine
except:
	pass
import uos
from tools import logger,filesystem,info

class SdCard:
	""" Manage the sdcard """
	opened = [False]
	mountpoint = [""]
	slot = [{}]

	@staticmethod
	def set_slot(**slot):
		""" Set the default sdcard slot
		- slot :  selects which of the available interfaces to use. Leaving this unset will select the default interface.
		- width : selects the bus width for the SD/MMC interface.
		- cd : can be used to specify a card-detect pin.
		- wp : can be used to specify a write-protect pin.
		- sck : can be used to specify an SPI clock pin.
		- miso : can be used to specify an SPI miso pin.
		- mosi : can be used to specify an SPI mosi pin.
		- cs : can be used to specify an SPI chip select pin.
		- freq : selects the SD/MMC interface frequency in Hz (only supported on the ESP32).
		(look doc http://docs.micropython.org/en/latest/library/machine.SDCard.html?highlight=sdcard) """
		SdCard.slot[0] = slot

	@staticmethod
	def get_max_size():
		""" Return the maximal size of sdcard """
		if SdCard.is_mounted():
			status = uos.statvfs(SdCard.get_mountpoint())
			return status[1]*status[2]
		else:
			return 0

	@staticmethod
	def get_free_size():
		""" Return the free size of sdcard """
		if SdCard.is_mounted():
			status = uos.statvfs(SdCard.get_mountpoint())
			return status[0]*status[3]
		else:
			return 0

	@staticmethod
	def is_mounted():
		""" Indicates if the sd card is mounted """
		return SdCard.opened[0]

	@staticmethod
	def is_available():
		""" Indicates if the sd card is available on device """
		if "slot" in SdCard.slot[0]:
			if SdCard.slot[0]["slot"] is None:
				return False
		return True

	@staticmethod
	def get_mountpoint():
		""" Return the mount point """
		return SdCard.mountpoint[0]

	@staticmethod
	def mount(mountpoint = "/sd"):
		""" Mount sd card """
		result = False
		if SdCard.is_mounted() is False and mountpoint != "/" and mountpoint != "":
			if SdCard.is_available():
				if filesystem.ismicropython():

					try:
						# If the sdcard not already mounted
						if uos.statvfs("/") == uos.statvfs(mountpoint):
							uos.mount(machine.SDCard(**(SdCard.slot[0])), mountpoint)
							SdCard.mountpoint[0] = mountpoint
							SdCard.opened[0]= True
							result = True
					except Exception as err:
						info.increase_issues_counter()
						logger.syslog("Cannot mount %s"%mountpoint)
				else:
					SdCard.mountpoint[0] = mountpoint[1:]
					SdCard.opened[0] = True
					result = True
			else:
				logger.syslog("SdCard disabled")
				if filesystem.ismicropython():
					SdCard.mountpoint[0] = "/data"
				else:
					from os import getcwd
					SdCard.mountpoint[0] = "%s/data"%getcwd()
				SdCard.opened[0] = True
				filesystem.makedir(SdCard.mountpoint[0], True)
				result = True
		elif SdCard.is_mounted():
			if filesystem.ismicropython():
				if SdCard.is_available():
					if mountpoint == SdCard.get_mountpoint():
						result = True
				else:
					result = True
			else:
				result = True
		return result

	@staticmethod
	def create_file(directory, filename, mode="w"):
		""" Create file with directory """
		result = None
		filepath = directory + "/" + filename
		directories = [directory]
		direct = directory
		while 1:
			parts = filesystem.split(direct)

			if parts[1] == "" or parts[0] == "":
				break
			directories.append(parts[0])
			direct = parts[0]

		if "/" in directories:
			directories.remove("/")
		if SdCard.mountpoint[0] in directories:
			directories.remove(SdCard.mountpoint[0])

		newdirs = []
		for l in range(len(directories)):
			part = directories[:l]
			part.reverse()
			newdirs.append(part)
		directories.reverse()
		newdirs.append(directories)

		for directories in newdirs:
			for direct in directories:
				try:
					uos.mkdir(direct)
				except OSError as err:
					if err.args[0] not in [2,17]:
						logger.syslog(err)
						break
			try:
				result = open(filepath,mode)
				break
			except OSError as err:
				if err.args[0] not in [2,17]:
					logger.syslog(err)
					break
		return result

	@staticmethod
	def is_not_enough_space(low):
		""" Indicates if remaining space is not sufficient """
		free = SdCard.get_free_size()
		total = SdCard.get_max_size()
		if low:
			if SdCard.is_available():
				threshold = 5
			else:
				threshold = 5
		else:
			if SdCard.is_available():
				threshold = 8
			else:
				threshold = 25

		if free < 0 or total < 0:
			return True

		if free < 32*1024*4:
			return True
		else:
			return ((free * 100 // total) <= threshold)

	@staticmethod
	def save(directory, filename, data):
		""" Save file on sd card """
		result = False
		if SdCard.is_mounted():
			file = None
			if SdCard.is_not_enough_space(low=True) is False:
				try:
					file = SdCard.create_file(SdCard.get_mountpoint() + "/" + directory, filename, "w")
					file.write(data)
					file.close()
					result = True
				except OSError as err:
					logger.syslog(err, "Cannot save %s/%s/%s"%(SdCard.get_mountpoint(), directory, filename))
					# If sd card not responding properly
					if err.errno == 2:
						info.increase_issues_counter()
				except Exception as err:
					logger.syslog(err, "Cannot save %s/%s/%s"%(SdCard.get_mountpoint(), directory, filename))
				finally:
					if file is not None:
						file.close()
			else:
				if SdCard.is_available() is False:
					result = True
		return result
