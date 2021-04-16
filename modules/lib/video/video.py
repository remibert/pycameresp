# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class to manage the camera of the ESP32CAM.
This requires the modified firmware. 
I added in the firmware the possibility of detecting movements, 
as well as a lot of adjustment on the camera, not available on the other firmware that manages the esp32cam.
"""
import sys
import machine
import camera
import time
from tools import useful
from tools import jsonconfig

class CameraConfig:
	streamingBase = [0]
	""" Class that collects the camera rendering configuration """
	def __init__(self):
		""" Constructor """
		self.framesize  = b"640x480"
		self.pixformat  = b"JPEG"
		self.quality    = 10
		self.brightness = 0
		self.contrast   = 0
		self.saturation = 0
		self.hmirror    = False
		self.vflip      = False
		self.streamingBase[0] = self.streamingBase[0] + 1
		self.streamingId = self.streamingBase[0]

	def save(self, file = None):
		""" Save configuration """
		result = jsonconfig.save(self, file)
		return result

	def update(self, params):
		""" Update configuration """
		result = jsonconfig.update(self, params)
		return result

	def load(self, file = None):
		""" Load configuration """
		result = jsonconfig.load(self, file)
		return result

class Motion:
	""" Class motion detection returned by the detect function """
	def __init__(self, motion):
		""" Constructor with motion object """
		self.motion = motion

	def deinit (self):
		""" Destructor """
		self.motion.deinit()

	def extract(self):
		""" Extract the full content of motion """
		return self.motion.extract()

	def compare(self, other):
		""" Compare image to detect motion """
		return self.motion.compare(other.motion)

	def setErrorHue(self, hue):
		""" Define the error tolered in the compare method on hue """
		self.motion.setErrorHue(hue)

	def setErrorLight(self, light):
		""" Define the error tolered in the compare method on light """
		self.motion.setErrorLight(light)

	def setErrorSaturation(self,saturation):
		""" Define the error tolered in the compare method on  saturation """
		self.motion.setErrorSaturation(saturation)

	def getImage(self):
		""" Return the jpeg buffer of motion """
		return self.motion.getImage()

	def getFeature(self):
		""" Return (mean, min, max light, mean, min, max, saturation, total count) """
		return self.getFeature()

class Camera:
	""" Singleton class to manage the camera """
	reserved = [False]
	opened = False

	@staticmethod
	def open():
		""" Open the camera """
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
				print("Failed to initialized camera reboot")
				machine.reset()
			
			# Photo on 800x600, motion detection / 8 (100x75), each square detection 8x8 (12.5 x 9.375)
			Camera.opened = True

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
		result = None
		if Camera.opened:
			retry = 10
			while 1:
				if retry == 0:
					print("Reset")
					machine.reset()
				try:
					# camera.quality(32)
					result = camera.capture()
					break
				except ValueError:
					print("Failed to get capture %d retry before reset"%retry)
					retry += 1
					time.sleep(0.5)
		return result

	@staticmethod
	def reserve():
		""" Reserve the camera, is used to stream the output of the camera
		to the web page. It stop the motion detection during this phase """
		if Camera.reserved[0] == False:
			Camera.reserved[0] = True
			return True
		return False

	@staticmethod
	def unreserve():
		""" Unreserve the camera """
		if Camera.reserved[0] == True:
			Camera.reserved[0] = False
			return True
		return False

	@staticmethod
	def isReserved():
		""" Indicates if the camera is reserved or no """
		return Camera.reserved[0]

	@staticmethod
	def motion():
		""" Get the motion informations. 
		This contains a jpeg image, with matrices of the different color RGB """
		result = None
		if Camera.opened:
			retry = 10
			while 1:
				if retry == 0:
					print("Reset")
					machine.reset()
				try:
					result = camera.motion()
					break
				except ValueError:
					print("Failed to get motion %d retry before reset"%retry)
					retry += 1
					time.sleep(0.5)
		return result

	@staticmethod
	def compare(image1, image2):
		""" Compare motion images """
		return camera.compare(image1, image2)

	@staticmethod
	def framesize(resolution):
		""" Configure the frame size """
		val = None
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
	def pixformat(format):
		""" Change the format of image """
		val = None
		if format == b"RGB565"    : val=camera.PIXFORMAT_RGB565
		if format == b"YUV422"    : val=camera.PIXFORMAT_YUV422
		if format == b"GRAYSCALE" : val=camera.PIXFORMAT_GRAYSCALE
		if format == b"JPEG"      : val=camera.PIXFORMAT_JPEG
		if format == b"RGB888"    : val=camera.PIXFORMAT_RGB888
		if format == b"RAW"       : val=camera.PIXFORMAT_RAW
		if format == b"RGB444"    : val=camera.PIXFORMAT_RGB444
		if format == b"RGB555"    : val=camera.PIXFORMAT_RGB555
		if Camera.opened and val != None:
			print("Pixformat %s"%useful.tostrings(format))
			camera.pixformat(val)
		else:
			print("Pixformat not set")
	
	@staticmethod
	def quality(val=None):
		""" Configure the compression """
		if Camera.opened:
			# print("Quality %d"%val)
			return camera.quality(val)
		return None

	@staticmethod
	def brightness(val=None):
		""" Change the brightness """
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
		if Camera.opened:
			# print("Sharpness %d"%val)
			return camera.sharpness(val)
		return None

	@staticmethod
	def hmirror(val=None):
		""" Set horizontal mirroring """
		if Camera.opened:
			# print("Hmirror %d"%val)
			return camera.hmirror(val)
		return None

	@staticmethod
	def vflip(val=None):
		""" Set the vertical flip """
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
