# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Class to manage the camera of the ESP32CAM.
This requires the modified firmware.
I added in the firmware the possibility of detecting movements,
as well as a lot of adjustment on the camera, not available on the other firmware that manages the esp32cam.
"""
# pylint: disable=multiple-statements
import time
import uasyncio
import os
import tools.info
import tools.system
import tools.jsonconfig
import tools.logger
if tools.info.iscamera():
	import camera

class CameraConfig(tools.jsonconfig.JsonConfig):
	""" Class that collects the camera rendering configuration """
	def __init__(self):
		""" Constructor """
		tools.jsonconfig.JsonConfig.__init__(self)
		self.activated  = True
		self.framesize  = b"640x480"
		self.pixformat  = b"JPEG"
		self.quality    = 25
		self.brightness = 0
		self.contrast   = 0
		self.saturation = 0
		self.hmirror    = False
		self.vflip      = False
		self.flash_level = 0

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
			if timeout < 0:
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
			if self.identifier is None:
				# If suspension not required
				if suspension is None:
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
	new_failed = [0]
	config = None
	flash_enabled = [True]
	aquisition = [False]

	@staticmethod
	def gpio_config(**kwargs):
		""" Configure the structure for camera initialization. It must be done before the first call of Camera.open.
			The defaults values are for ESP32CAM.
			- pin_pwdn           : GPIO pin for camera power down line
			- pin_reset          : GPIO pin for camera pin_reset line
			- pin_xclk           : GPIO pin for camera XCLK line
			- pin_sscb_sda       : GPIO pin for camera SDA line (SIOD)
			- pin_sscb_scl       : GPIO pin for camera SCL line (SIOC)
			- pin_d7             : GPIO pin for camera D7 or Y9 line
			- pin_d6             : GPIO pin for camera D6 or Y8 line
			- pin_d5             : GPIO pin for camera D5 or Y7 line
			- pin_d4             : GPIO pin for camera D4 or Y6 line
			- pin_d3             : GPIO pin for camera D3 or Y5 line
			- pin_d2             : GPIO pin for camera D2 or Y4 line
			- pin_d1             : GPIO pin for camera D1 or Y3 line
			- pin_d0             : GPIO pin for camera D0 or Y2 line
			- pin_vsync          : GPIO pin for camera VSYNC line
			- pin_href           : GPIO pin for camera HREF line
			- pin_pclk           : GPIO pin for camera PCLK line
			- xclk_freq_hz       : Frequency of XCLK signal, in Hz. Either 20KHz or 10KHz for OV2640 double FPS (Experimental)
			- ledc_timer         : LEDC timer to be used for generating XCLK
			- ledc_channel       : LEDC channel to be used for generating XCLK
			- pixel_format       : Format of the pixel data: PIXFORMAT_ + YUV422|GRAYSCALE|RGB565|JPEG
			- frame_size         : Size of the output image: FRAMESIZE_ + QVGA|CIF|VGA|SVGA|XGA|SXGA|UXGA
			- jpeg_quality       : Quality of JPEG output. 0-63 lower means higher quality
			- fb_count           : Number of frame buffers to be allocated. If more than one, then each frame will be acquired (double speed)
			- flash_led          : GPIO pin for flash led or 0 to disable 
			- grab_mode          : 0=CAMERA_GRAB_WHEN_EMPTY, 1=CAMERA_GRAB_LATEST
			- fb_location        : 0=CAMERA_FB_IN_PSRAM, 1=CAMERA_FB_IN_DRAM
"""
		Camera.get_config()
		if Camera.is_activated():
			camera.configure(**kwargs)

	@staticmethod
	def open():
		""" Open the camera """
		Camera.get_config()
		if Camera.is_activated():
			result = True
			if Camera.opened is False:
				for i in range(10):
					res = camera.init()
					if res is False:
						# print("Camera not initialized")
						camera.deinit()
						time.sleep(0.5)
					else:
						break
				else:
					result = False

				if result:
					# Photo on 800x600, motion detection / 8 (100x75), each square detection 8x8 (12.5 x 9.375)
					Camera.opened = True
					Camera.aquisition[0] = False
		else:
			result = False
		return result

	@staticmethod
	def get_stat():
		""" Statistic """
		return Camera.success[0], Camera.failed[0]

	@staticmethod
	def reset_stat():
		""" Reset statistic """
		Camera.success[0] = 0
		Camera.failed [0] = 0
		Camera.new_failed[0] = 0

	@staticmethod
	def close():
		""" Close the camera """
		if Camera.opened is True:
			camera.deinit()
			Camera.opened = False

	@staticmethod
	def reset():
		""" Reset the camera """
		if Camera.opened is True:
			camera.reset()

	@staticmethod
	def is_opened():
		""" Indicates if the camera opened """
		return Camera.opened

	@staticmethod
	def capture():
		""" Capture an image on the camera """
		Camera.aquisition[0] = True
		return Camera.retry(camera.capture)

	@staticmethod
	def motion():
		""" Get the motion informations.
		This contains a jpeg image, with matrices of the different color RGB """
		Camera.aquisition[0] = True
		return Camera.retry(camera.motion)

	@staticmethod
	def flash(level=0):
		""" Start or stop the flash """
		if Camera.flash_enabled[0]:
			camera.flash(level)

	@staticmethod
	def set_flash(state):
		""" On the esp32cam, we use the output of the led flash to communicate with the dfplayer, 
		and this disrupts the operation, then we can turn it off """
		Camera.flash_enabled[0] = state

	@staticmethod
	def retry(callback):
		""" Retry camera action and manage error """
		result = None
		if Camera.opened:
			retry = 10
			while 1:
				if retry <= 0:
					tools.system.reboot("Reboot forced after camera problem")
				try:
					result = callback()
					Camera.success[0] += 1
					break
				except ValueError:
					Camera.failed[0] += 1
					Camera.new_failed[0] += 1
					if retry <= 3:
						tools.logger.syslog("Failed to get image %d retry before reset"%retry)
					retry -= 1
					time.sleep(0.5)
			total = Camera.success[0] + Camera.failed[0]
			STAT_CAMERA=20000
			if (total % STAT_CAMERA) == 0:
				if Camera.success[0] != 0:
					new_failed = 100.-((Camera.new_failed[0]*100)/STAT_CAMERA)
					failed    = 100.-((Camera.failed[0]*100)/total)
				else:
					new_failed = 0.
					failed    = 0.
				tools.logger.syslog("Camera stat : last %-3.1f%%, total %-3.1f%% success on %d"%(new_failed, failed, total))
				Camera.new_failed[0] = 0
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
	def is_modified():
		""" Indicates that the camera configuration has been changed """
		return Camera.modified[0]

	@staticmethod
	def clear_modified():
		""" Reset the indicator of configuration modification """
		Camera.modified[0] = False

	@staticmethod
	def reinit():
		""" Close and open camera if get image previously asked, it avoid a DMA problem """
		if Camera.opened:
			if Camera.aquisition[0] is True:
				if "FREENOVE CAM" in os.uname().machine:
					Camera.close()
					Camera.open()

	@staticmethod
	def framesize(resolution=None):
		""" Configure the frame size """
		result = None
		val = None
		Camera.modified[0] = True
		if   resolution == b"UXGA"  or resolution == b"1600x1200" :val = camera.FRAMESIZE_UXGA
		elif resolution == b"SXGA"  or resolution == b"1280x1024" :val = camera.FRAMESIZE_SXGA
		elif resolution == b"XGA"   or resolution == b"1024x768"  :val = camera.FRAMESIZE_XGA
		elif resolution == b"SVGA"  or resolution == b"800x600"   :val = camera.FRAMESIZE_SVGA
		elif resolution == b"VGA"   or resolution == b"640x480"   :val = camera.FRAMESIZE_VGA
		elif resolution == b"CIF"   or resolution == b"400x296"   :val = camera.FRAMESIZE_CIF
		elif resolution == b"QVGA"  or resolution == b"320x240"   :val = camera.FRAMESIZE_QVGA
		elif resolution == b"HQVGA" or resolution == b"240x176"   :val = camera.FRAMESIZE_HQVGA
		elif resolution == b"QQVGA" or resolution == b"160x120"   :val = camera.FRAMESIZE_QQVGA
		if Camera.opened:
			# print("Framesize %s"%strings.tostrings(resolution))
			result = camera.framesize(val)
			if result is False and val is not None:
				Camera.reinit()
				result = camera.framesize(val)
		return result

	@staticmethod
	def pixformat(format_=None):
		""" Change the format of image """
		result = None
		Camera.modified[0] = True
		val = None
		if   format_ == b"RGB565"    : val=camera.PIXFORMAT_RGB565
		elif format_ == b"YUV422"    : val=camera.PIXFORMAT_YUV422
		elif format_ == b"GRAYSCALE" : val=camera.PIXFORMAT_GRAYSCALE
		elif format_ == b"JPEG"      : val=camera.PIXFORMAT_JPEG
		elif format_ == b"RGB888"    : val=camera.PIXFORMAT_RGB888
		elif format_ == b"RAW"       : val=camera.PIXFORMAT_RAW
		elif format_ == b"RGB444"    : val=camera.PIXFORMAT_RGB444
		elif format_ == b"RGB555"    : val=camera.PIXFORMAT_RGB555
		if Camera.opened:
			# print("Pixformat %s"%strings.tostrings(format_))
			result = camera.pixformat(val)
			if result is False and val is not None:
				Camera.reinit()
				result = camera.pixformat(val)
		return result

	@staticmethod
	def quality(val=None, modified=True):
		""" Configure the compression """
		result = None
		Camera.modified[0] = modified
		if Camera.opened:
			# print("Quality %d"%val)
			result = camera.quality(val)
			if result is False and val is not None:
				Camera.reinit()
				result = camera.quality(val)
		return result

	@staticmethod
	def brightness(val=None):
		""" Change the brightness """
		result = None
		Camera.modified[0] = True
		if Camera.opened:
			# print("Brightness %d"%val)
			result = camera.brightness(val)
			if result is False and val is not None:
				Camera.reinit()
				result = camera.brightness(val)
		return result

	@staticmethod
	def contrast(val=None):
		""" Change the contrast """
		result = None
		Camera.modified[0] = True
		if Camera.opened:
			# print("Contrast %d"%val)
			result = camera.contrast(val)
			if result is False and val is not None:
				Camera.reinit()
				result = camera.contrast(val)
		return result

	@staticmethod
	def saturation(val=None):
		""" Change the saturation """
		result = None
		Camera.modified[0] = True
		if Camera.opened:
			# print("Saturation %d"%val)
			result = camera.saturation(val)
			if result is False and val is not None:
				Camera.reinit()
				result = camera.saturation(val)
		return result

	@staticmethod
	def sharpness(val=None):
		""" Change the sharpness """
		result = None
		Camera.modified[0] = True
		if Camera.opened:
			# print("Sharpness %d"%val)
			result = camera.sharpness(val)
			if result is False and val is not None:
				Camera.reinit()
				result = camera.sharpness(val)
		return result

	@staticmethod
	def hmirror(val=None):
		""" Set horizontal mirroring """
		result = None
		Camera.modified[0] = True
		if Camera.opened:
			# print("Hmirror %d"%val)
			result = camera.hmirror(val)
			if result is False and val is not None:
				Camera.reinit()
				result = camera.hmirror(val)
		return result

	@staticmethod
	def vflip(val=None):
		""" Set the vertical flip """
		result = None
		Camera.modified[0] = True
		if Camera.opened:
			# print("Vflip %d"%val)
			result = camera.vflip(val)
			if result is False and val is not None:
				Camera.reinit()
				result = camera.vflip(val)
		return result

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
			Camera.flash     (config.flash_level)

	@staticmethod
	def get_config():
		""" Reload configuration if it changed """
		if Camera.config is None:
			Camera.config = CameraConfig()
			if Camera.config.load() is False:
				Camera.config.save()
		else:
			Camera.config.refresh()
		return Camera.config

	@staticmethod
	def is_activated():
		""" Indicates if the camera is configured to be activated """
		if Camera.config is None:
			Camera.get_config()
		if Camera.config is not None:
			return Camera.config.activated
		else:
			return False
