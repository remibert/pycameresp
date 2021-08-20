# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class to manage the camera of the ESP32CAM.
This requires the modified firmware. 
I added in the firmware the possibility of detecting movements, 
as well as a lot of adjustment on the camera, not available on the other firmware that manages the esp32cam.
"""
import camera
import time
import uasyncio
from tools import useful
from tools import jsonconfig

class CameraConfig(jsonconfig.JsonConfig):
	""" Class that collects the camera rendering configuration """
	def __init__(self):
		""" Constructor """
		jsonconfig.JsonConfig.__init__(self)
		self.framesize  = b"640x480"
		self.pixformat  = b"JPEG"
		self.quality    = 25
		self.brightness = 0
		self.contrast   = 0
		self.saturation = 0
		self.hmirror    = False
		self.vflip      = False

class Motion:
	""" Class motion detection returned by the detect function """
	def __init__(self, motion):
		""" Constructor with motion object_ """
		self.motion = motion

	def deinit (self):
		""" Destructor """
		self.motion.deinit()

	def extract(self):
		""" Extract the full content of motion """
		return self.motion.extract()

	def compare(self, other, extractShape):
		""" Compare image to detect motion """
		return self.motion.compare(other.motion, extractShape)

	def configure(self, param):
		""" Configure the motion detection """
		self.motion.configure(param)

	def getImage(self):
		""" Return the jpeg buffer of motion """
		return self.motion.getImage()

class Reservation:
	""" Manage the camera reservation """
	def __init__(self):
		""" Constructor """
		self.identifier = None
		self.count = 0
		self.lock = uasyncio.Lock()
		self.suspended = 0

	async def reserve(self, object_, timeout=0, suspension=None):
		""" Wait the ressource and reserve """
		result = False
		# Wait 
		while True:
			result = await self.acquire(object_, suspension)
			if result:
				break
			timeout -= 1
			if timeout <= 0:
				break
			await uasyncio.sleep_ms(1000)
		return result

	async def acquire(self, object_, suspension=None):
		""" Reserve the camera, is used to stream the output of the camera
		to the web page. It stop the motion detection during this phase """
		result = False
		await self.lock.acquire()
		identifier = id(object_)
		try:
			# If not reserved
			if self.identifier == None:
				# If suspension not required
				if suspension == None:
					# If previous suspension ended
					if self.suspended <= 0:
						# Reserve
						self.identifier = identifier
						self.count = 1
						self.suspended = 0
						result = True
					else:
						# Decrease suspension counter
						self.suspended -= 1
				else:
					# Reserve
					self.identifier = identifier
					self.count = 1
					self.suspended = suspension
					result = True
			# If already reserved by the current object_
			elif self.identifier == identifier:
				# Increase reservation counter
				self.count += 1
				self.suspended = suspension
				result = True
		finally:
			self.lock.release()
		return result

	async def unreserve(self, object_):
		""" Unreserve the camera """
		result = False
		await self.lock.acquire()
		identifier = id(object_)
		try:
			if self.identifier == identifier:
				if self.count <= 1:
					self.count = 0
					self.identifier = None
				else:
					self.count -= 1
				result = True
		finally:
			self.lock.release()
		return result

class Camera:
	""" Singleton class to manage the camera """
	reservation = Reservation()
	opened = False
	lock = uasyncio.Lock()
	modified = [False]
	success = [0]
	failed  = [0]
	newFailed = [0]

	@staticmethod
	def open():
		""" Open the camera """
		result = True
		if Camera.opened == False:
			for i in range(10):
				res = camera.init()
				if res == False:
					print("Camera not initialized")
					camera.deinit()
					time.sleep(0.5)
				else:
					break
			else:
				result = False

			if result:
				# Photo on 800x600, motion detection / 8 (100x75), each square detection 8x8 (12.5 x 9.375)
				Camera.opened = True
		return result

	@staticmethod
	def getStat():
		""" Statistic """
		return Camera.success[0], Camera.failed[0]

	@staticmethod
	def resetStat():
		""" Reset statistic """
		Camera.success[0] = 0
		Camera.failed [0] = 0
		Camera.newFailed[0] = 0

	@staticmethod
	def close():
		""" Close the camera """
		if Camera.opened == True:
			camera.deinit()
			Camera.opened = False

	@staticmethod
	def isOpened():
		""" Indicates if the camera opened """
		return Camera.opened

	@staticmethod
	def capture():
		""" Capture an image on the camera """
		return Camera.retry(camera.capture)

	@staticmethod
	def motion():
		""" Get the motion informations. 
		This contains a jpeg image, with matrices of the different color RGB """
		return Camera.retry(camera.motion)

	@staticmethod
	def retry(callback):
		""" Retry camera action and manage error """
		result = None
		if Camera.opened:
			retry = 10
			while 1:
				if retry <= 0:
					useful.reboot("Reboot forced after camera problem")
				try:
					result = callback()
					Camera.success[0] += 1
					break
				except ValueError:
					Camera.failed[0] += 1
					Camera.newFailed[0] += 1
					if retry <= 3:
						useful.syslog("Failed to get image %d retry before reset"%retry)
					retry -= 1
					time.sleep(0.5)
			total = Camera.success[0] + Camera.failed[0]
			if (total % 5000) == 0:
				if Camera.success[0] != 0:
					newFailed = ((Camera.newFailed[0]*100)/Camera.success[0])
					failed    = ((Camera.failed[0]*100)/Camera.success[0])
				else:
					newFailed = 0.
					failed    = 0.
				useful.syslog("Camera failed : Last %-3.1f%%, All %-3.1f%% on %d"%(newFailed, failed, total))
				Camera.newFailed[0] = 0
		return result

	@staticmethod
	async def reserve(object_, timeout=0, suspension=None):
		""" Reserve the camera, is used to stream the output of the camera
		to the web page. It stop the motion detection during this phase """
		return await Camera.reservation.reserve(object_, timeout, suspension)

	@staticmethod
	async def unreserve(object_):
		""" Unreserve the camera """
		return await Camera.reservation.unreserve(object_)

	@staticmethod
	def isModified():
		""" Indicates that the camera configuration has been changed """
		return Camera.modified[0]

	@staticmethod
	def clearModified():
		""" Reset the indicator of configuration modification """
		Camera.modified[0] = False

	@staticmethod
	def framesize(resolution):
		""" Configure the frame size """
		val = None
		Camera.modified[0] = True
		if resolution == b"UXGA"  or resolution == b"1600x1200" :val = camera.FRAMESIZE_UXGA
		if resolution == b"SXGA"  or resolution == b"1280x1024" :val = camera.FRAMESIZE_SXGA
		if resolution == b"XGA"   or resolution == b"1024x768"  :val = camera.FRAMESIZE_XGA
		if resolution == b"SVGA"  or resolution == b"800x600"   :val = camera.FRAMESIZE_SVGA
		if resolution == b"VGA"   or resolution == b"640x480"   :val = camera.FRAMESIZE_VGA
		if resolution == b"CIF"   or resolution == b"400x296"   :val = camera.FRAMESIZE_CIF
		if resolution == b"QVGA"  or resolution == b"320x240"   :val = camera.FRAMESIZE_QVGA
		if resolution == b"HQVGA" or resolution == b"240x176"   :val = camera.FRAMESIZE_HQVGA
		if resolution == b"QQVGA" or resolution == b"160x120"   :val = camera.FRAMESIZE_QQVGA
		if Camera.opened and val != None:
			print("Framesize %s"%useful.tostrings(resolution))
			camera.framesize(val)
		else:
			print("Framesize not set")

	@staticmethod
	def pixformat(format_):
		""" Change the format of image """
		Camera.modified[0] = True
		val = None
		if format_ == b"RGB565"    : val=camera.PIXFORMAT_RGB565
		if format_ == b"YUV422"    : val=camera.PIXFORMAT_YUV422
		if format_ == b"GRAYSCALE" : val=camera.PIXFORMAT_GRAYSCALE
		if format_ == b"JPEG"      : val=camera.PIXFORMAT_JPEG
		if format_ == b"RGB888"    : val=camera.PIXFORMAT_RGB888
		if format_ == b"RAW"       : val=camera.PIXFORMAT_RAW
		if format_ == b"RGB444"    : val=camera.PIXFORMAT_RGB444
		if format_ == b"RGB555"    : val=camera.PIXFORMAT_RGB555
		if Camera.opened and val != None:
			print("Pixformat %s"%useful.tostrings(format_))
			camera.pixformat(val)
		else:
			print("Pixformat not set")
	
	@staticmethod
	def quality(val=None, modified=True):
		""" Configure the compression """
		Camera.modified[0] = modified
		if Camera.opened:
			# print("Quality %d"%val)
			return camera.quality(val)
		return None

	@staticmethod
	def brightness(val=None):
		""" Change the brightness """
		Camera.modified[0] = True
		if Camera.opened:
			# print("Brightness %d"%val)
			if camera.brightness() != val:
				return camera.brightness(val)
			else:
				return val
		return None

	@staticmethod
	def contrast(val=None):
		""" Change the contrast """
		Camera.modified[0] = True
		if Camera.opened:
			# print("Contrast %d"%val)
			if camera.contrast() != val:
				return camera.contrast(val)
			else:
				return val
		return None

	@staticmethod
	def saturation(val=None):
		""" Change the saturation """
		Camera.modified[0] = True
		if Camera.opened:
			# print("Saturation %d"%val)
			if camera.saturation() != val:
				return camera.saturation(val)
			else:
				return val
		return None

	@staticmethod
	def sharpness(val=None):
		""" Change the sharpness """
		Camera.modified[0] = True
		if Camera.opened:
			# print("Sharpness %d"%val)
			return camera.sharpness(val)
		return None

	@staticmethod
	def hmirror(val=None):
		""" Set horizontal mirroring """
		Camera.modified[0] = True
		if Camera.opened:
			# print("Hmirror %d"%val)
			return camera.hmirror(val)
		return None

	@staticmethod
	def vflip(val=None):
		""" Set the vertical flip """
		Camera.modified[0] = True
		if Camera.opened:
			# print("Vflip %d"%val)
			return camera.vflip(val)
		return None

	@staticmethod
	def configure(config):
		""" Configure the camera """
		if Camera.opened:
			Camera.pixformat (config.pixformat)
			Camera.framesize (config.framesize)
			Camera.quality   (config.quality)
			Camera.brightness(config.brightness)
			Camera.contrast  (config.contrast)
			Camera.saturation(config.saturation)
			Camera.hmirror   (config.hmirror)
			Camera.vflip     (config.vflip)
