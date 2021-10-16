# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Sdcard management class """
try:
	import machine
except:
	pass
import uos
from tools import useful

class SdCard:
	""" Manage the sdcard """
	opened = [False]
	mountpoint = [""]

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
	def get_mountpoint():
		""" Return the mount point """
		return SdCard.mountpoint[0]

	@staticmethod
	def mount(mountpoint = "/sd"):
		""" Mount sd card """
		result = False
		if SdCard.is_mounted() is False and mountpoint != "/" and mountpoint != "":
			if useful.ismicropython():
				try:
					# If the sdcard not already mounted
					if uos.statvfs("/") == uos.statvfs(mountpoint):
						uos.mount(machine.SDCard(), mountpoint)
						SdCard.mountpoint[0] = mountpoint
						SdCard.opened[0]= True
						result = True
				except Exception as err:
					useful.syslog("Cannot mount %s"%mountpoint)
			else:
				SdCard.mountpoint[0] = mountpoint[1:]
				SdCard.opened[0] = True
				result = True
		elif SdCard.is_mounted():
			if useful.ismicropython():
				if mountpoint == SdCard.get_mountpoint():
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
			parts = useful.split(direct)

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
						useful.syslog(err)
						break
			try:
				result = open(filepath,mode)
				break
			except OSError as err:
				if err.args[0] not in [2,17]:
					useful.syslog(err)
					break
		return result

	@staticmethod
	def save(directory, filename, data):
		""" Save file on sd card """
		result = False
		if SdCard.is_mounted():
			file = None
			try:
				file = SdCard.create_file(SdCard.get_mountpoint() + "/" + directory, filename, "w")
				file.write(data)
				file.close()
				result = True
			except Exception as err:
				useful.syslog(err, "Cannot save %s/%s/%s"%(SdCard.get_mountpoint(), directory, filename))
			finally:
				if file is not None:
					file.close()
		return result
