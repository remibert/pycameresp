# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Motion detection only work with ESP32CAM (Requires specially modified ESP32CAM firmware to handle motion detection.) """
import sys
import machine
import uos
try:
	import camera
except:
	pass
import uasyncio
import video
import time
from tools import useful
from tools import jsonconfig

class MotionConfig:
	""" Configuration class of motion detection """
	def __init__(self):
		# Indicates if the motion is activated
		self.activated = False

		# Number of images before camera stabilization
		self.stabilizationCamera=6

		# Error range ignore rgb modification
		self.rbgErrorRange=12

		# Max images in motion historic
		self.maxMotionImages=10

		# Min and max threshold detection for rgb change
		self.minRgbDetection=9
		self.maxRgbDetection=80

		# Glitch threshold of image ignored (sometime the camera bug)
		self.thresholdGlitch=2

		# Threshold of minimum image to detect motion
		self.thresholdMotion=3
  
		# Awake time on battery (seconds)
		self.awakeTime = 15

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

class SdCard:
	""" Class to mount the sd card """
	def __init__(self, mountpoint="/sd"):
		self.opened = False
		self.mountpoint = mountpoint
		self.open()
		
	def __del__(self):
		self.close()

	def open(self):
		""" Open and mount sd card """
		if self.opened == False:
			try:
				uos.mount(machine.SDCard(), self.mountpoint)
				print("Mount %s"%self.mountpoint)
				self.opened = True
			except Exception as error:
				# print(exception(error))
				print("Cannot mount %s"%self.mountpoint)
		return self.opened

	def close(self):
		""" Close and unmount sd card """
		if self.opened == True:
			print("Umount %s"%self.mountpoint)
			uos.umount(self.mountpoint)
	
	def save(self, filename, data):
		""" Save file on sd card """
		if self.open():
			filename = "%s/%s"%(self.mountpoint,filename)
			try:
				file = open(filename,"wb")
				file.write(data)
				file.close()
			except Exception as error:
				# print(exception(error))
				print("Cannot save %s"%filename)

class ImageMotion:
	""" Class managing a motion detection image """
	baseIndex = [0]
	motionBaseId = [0]
	def __init__(self, image, config):
		self.image       = image[0]
		self.reds        = image[1]
		self.greens      = image[2]
		self.blues       = image[3]
		self.hues        = image[4]
		self.saturations = image[5]
		self.lights      = image[6]
		self.baseIndex[0] += 1
		self.index    = self.baseIndex[0]
		self.filename = None
		self.diff     = 0
		self.diffRgb  = (0,0,0)
		self.notified = False
		self.motionId = None
		self.date     = useful.dateToFilename()
		self.motionDetected = False
		self.config = config
	
	def setMotionId(self, motionId = None):
		""" Set the unique image identifier """
		if motionId == None:
			self.motionBaseId[0] += 1
			self.motionId = self.motionBaseId[0]
		else:
			if self.motionId == None:
				self.motionId = motionId
			else:
				print("Motion id already set")
	
	def getMotionId(self):
		""" Get the unique image identifier """
		return self.motionId

	def getFilename(self):
		""" Get the storage filename """
		return "%s (id=%d) (diff=%d).jpg"%(self.date, self.index, (self.diffRgb[0]+self.diffRgb[1]+self.diffRgb[2])//3)

	def save(self, sdcard):
		""" Save the image on sd card """
		if sdcard != None:
			sdcard.save(self.getFilename(), self.image)

	def compareComposite(self, current, previous):
		""" Compare two composite motion images to get differences """
		result = 0
		for i in range(len(current)):
			delta = current[i]-previous[i]
			if abs(delta) > self.config.rbgErrorRange:
				result += 1
		return result
	
	def compare(self, previous, set=False):
		""" Compare two motion images to get differences """
		reds        = self.compareComposite(self.reds,        previous.reds)
		greens      = self.compareComposite(self.greens,      previous.greens)
		blues       = self.compareComposite(self.blues,       previous.blues)
		if set:
			self.diff    = reds+greens+blues
			self.diffRgb = (reds,greens,blues)
		return (reds, greens, blues)

	def getMotionDetected(self):
		""" Get the motion detection status """
		return self.motionDetected
	
	def setMotionDetected(self):
		""" Set the motion detection status """
		self.motionDetected = True
	
	def get(self):
		""" Get the image captured """
		return self.image
	
	def getDifferences(self):
		""" Get the differences found with the previous image """
		return self.diff//3

	def resetDifferences(self):
		""" Reset the differences, used during the camera stabilization image """
		self.diff = 0
		self.diffRgb = (0,0,0)

class Motion:
	""" Class to manage the motion capture """
	def __init__(self, sdcard = None, config= None, onBattery=False, pirDetection=False):
		self.images = []
		self.sdcard = sdcard
		self.index  = 0
		self.config = config
		self.onBattery = onBattery
		self.pirDetection = pirDetection

	def open(self):
		""" Open camera """
		print("Open camera")
		video.Camera.open()
		self.resume()

	def resume(self):
		""" Resume the camera, restore the camera configuration after an interruption """
		video.Camera.framesize(b"SVGA")
		# video.Camera.framesize(b"XGA")
		# video.Camera.framesize(b"SXGA")
		video.Camera.pixformat(b"JPEG")
		video.Camera.quality(10)
		video.Camera.brightness(0)
		video.Camera.contrast(0)
		video.Camera.saturation(0)
		video.Camera.hmirror(0)
		video.Camera.vflip(0)

	def capture(self):
		""" Capture motion image """
		result = None
		retry = 10
		if len(self.images) >= self.config.maxMotionImages:
			image = self.images.pop()
			
			# If motion detected on image, on battery the first five images are sent
			if image.getMotionDetected() or (self.onBattery and self.pirDetection and image.index <= 3):
				# Notification of motion
				result = ("Intrusion %s"%image.getFilename(), image.get())
				print("Intrusion %s"%image.getFilename()[:-3])

				# Save image to sdcard
				image.save(self.sdcard)

		while 1:
			if retry == 0:
				print("Reset")
				machine.reset()

			try:
				image = ImageMotion(video.Camera.motion(), self.config)
				self.images.insert(0, image)
				self.index += 1
				break
			except ValueError:
				print("Failed to get motion %d try before reset"%retry)
				retry += 1
				time.sleep(0.5)
		return result

	def isStabilized(self):
		# If the PIR detection force the stabilization
		if self.pirDetection == True:
			stabilized = True
		# If the camera not stabilized
		elif len(self.images) < self.config.stabilizationCamera:
			stabilized = False
		else:
			stabilized = True
		return stabilized

	def compare(self):
		""" Compare all images captured and search differences """
		differences = {}
		if len(self.images) >= 2:
			current = self.images[0]
			
			# Compute the motion identifier
			for previous in self.images[1:]:
				reds, greens, blues = current.compare(previous, True)

				# If camera not stabilized
				if self.isStabilized() == False:
					# Reject the differences
					current.resetDifferences()
					break
				# If image seem equal to previous
				if ((reds+greens+blues)//3) <= self.config.minRgbDetection:
					# Reuse the motion identifier
					current.setMotionId(previous.motionId)
					break
			else:
				# Create new motion id
				current.setMotionId()

			# Compute the list of differences
			diffs = ""
			for image in self.images:
				differences.setdefault(image.getMotionId(), []).append(image.getMotionId())
				if image.getMotionId() != None:
					diffs += " %d:%d"%(image.getMotionId(), image.getDifferences())
			
			sys.stdout.write("\r%s %s    "%(useful.dateToString()[12:], diffs))
		return differences

	def detect(self):
		""" Detect motion """
		detected = False
		changePolling = False

		# Compute the list of differences
		differences = self.compare()

		# Too many differences found
		if len(list(differences.keys())) >= self.config.thresholdMotion:
			detected = True
			changePolling = True
		# If no differences
		elif len(list(differences.keys())) == 1:
			detected = False
		# If not enough differences
		elif len(list(differences.keys())) <= self.config.thresholdGlitch:
			detected = True
			changePolling = True
			# Check if it is a glitch
			for diff in differences.values():
				if len(diff) <= 1:
					print("%s Glitch (diff=%d)    "%(useful.dateToString()[12:], self.images[0].getDifferences()))
					# Glitch ignored
					detected = False
					break
		# Not detected
		else:
			detected = False

		if detected:
			# Mark all motion images
			for image in self.images:
				diff = image.getDifferences()
				# If image seem equal to previous
				if  diff > self.config.minRgbDetection and diff < self.config.maxRgbDetection:
					image.setMotionDetected()
		return detected, changePolling

async def sleep_ms(duration):
	""" Multiplatform sleep_ms """
	await uasyncio.sleep_ms(duration)

async def detectMotion(onBattery, pirDetection):
	""" Asynchronous motion detection main routine """
	from server   import asyncNotify, PushOverConfig
	from motion   import MotionConfig
	import wifi

	# Open push over notification object
	pushoverConfig = PushOverConfig()
	pushoverConfig.load()

	# Open motion configuration
	motionConfig      = MotionConfig()
	if motionConfig.load() == False:
		motionConfig.save()

	motion = None
	reloadConfig = 0
	previousReserved = None
	pollingFrequency = 200
	batteryLevel = -2
	if onBattery:
		if pirDetection == True:
			pollingFrequency = 3
		motionConfig.load()
		wifiOn = False
		startTime = time.time()
	else:
		wifiOn = True

	while True:
		# If the motion activated
		if motionConfig.activated:
			# If motion not initialized
			if motion == None:
				# The sdcard not available on battery
				if onBattery == True:
					sdcard = None
				else:
					sdcard = SdCard()
				motion = Motion(sdcard, motionConfig, onBattery, pirDetection)
				motion.open()

			# If camera available to detect motion
			if video.Camera.isReserved() == False:
				# If the camera previously reserved
				if previousReserved == True:
					# Restore camera motion configuration
					previousReserved = False
					motion.resume()
				try:
					# If camera not stabilized speed start
					if motion.isStabilized() == True:
						await sleep_ms(pollingFrequency)

					# If camera available to detect motion
					if video.Camera.isReserved() == False:
						# Capture motion image
						detection = motion.capture()

						# If camera not stabilized speed start
						if motion.isStabilized() == True:
							await sleep_ms(pollingFrequency)

					# If camera available to detect motion
					if video.Camera.isReserved() == False:
						# If motion detected
						if detection != None:
							# Notify motion with push over
							message, image = detection
							# On battery the wifi start after taking pictures
							if wifiOn == False:
								from server import start
								from tools import Battery
								start(withoutServer=True)
								wifiOn = True
								batteryLevel = Battery.getLevel()
							if batteryLevel >= 0:
								message = message [:-4] + " Bat %s %%"%batteryLevel
							await asyncNotify(pushoverConfig.user, pushoverConfig.token, message, image)
						# Detect motion
						detected, changePolling = motion.detect()

						# If motion found
						if changePolling == True:
							# Speed up the polling frequency
							pollingFrequency = 5
							startTime = time.time()
						else:
							# Slow down the polling frequency
							pollingFrequency = 300
				except Exception as err:
					print(useful.exception(err))
			else:
				# Camera buzy, motion capture suspended
				previousReserved = True
				print("Motion suspended")
				await sleep_ms(3000)
		else:
			# Motion capture disabled
			await sleep_ms(500)
		reloadConfig += 1

		# Reload configuration each 3 s
		if reloadConfig % 5 == 0:
			motionConfig.load()
		
		# If the battery mode activated
		if onBattery:
			# If the motion detection activated
			if motionConfig.activated:
				# Wait duration after the last detection
				if time.time() > startTime + motionConfig.awakeTime:
					import machine
					print("")
					print("####################################")
					print("# DEEP SLEEP TO WAIT PIR DETECTION #")
					print("####################################")
					machine.deepsleep(10000)

def start(loop=None, onBattery=True, pirDetection=False):
	""" Start the asynchronous motion detection """
	if useful.iscamera():
		loop.create_task(detectMotion(onBattery, pirDetection))
	pass
