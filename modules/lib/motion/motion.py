# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Motion detection only work with ESP32CAM (Requires specially modified ESP32CAM firmware to handle motion detection.) """
import sys
import machine
import uos
import re
try:
	import camera
except:
	pass
import uasyncio
import video
import time
from tools import useful, jsonconfig
import json
import server
from motion import presence
from motion import historic

class MotionConfig:
	""" Configuration class of motion detection """
	def __init__(self):
		# Indicates if the motion is activated
		self.activated = False

		# Suspend the motion detection when presence detected
		self.suspendOnPresence = True

		# Minimum difference contigous threshold to detect movement
		self.contigousDetection = 10

		# Awake time on battery (seconds)
		self.awakeTime = 120

		# Error range ignore hue modification (5%)
		self.hueErrorRange=18 

		# Error range ignore saturation modification (10%)
		self.saturationErrorRange=10

		# Error range ignore light modification (5%)
		self.lightErrorRange=5

		# Max images in motion historic
		self.maxMotionImages=10

		# Glitch threshold of image ignored (sometime the camera bug)
		self.thresholdGlitch=2

		# Threshold of minimum image to detect motion
		self.thresholdMotion=3

		# Number of images before camera stabilization
		self.stabilizationCamera=8

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

class ImageMotion:
	""" Class managing a motion detection image """
	baseIndex = [0]
	motionBaseId = [0]
	def __init__(self, motion, config):
		self.motion = motion
		self.baseIndex[0] += 1
		self.index    = self.baseIndex[0]
		self.filename = None
		self.motionId = None
		self.date     = useful.dateToString()
		self.filename = useful.dateToFilename()
		self.path     = useful.dateToPath()[:-1] + "0"
		self.motionDetected = False
		self.config = config
		self.comparison = None

	def deinit(self):
		""" Destructor """
		self.motion.deinit()
	
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
		return "%s D=%d"%(self.filename, self.getDiffCount())

	def getHtmlShapes(self):
		""" Get the html page with shapes on the image """
		html = b"""<script type='text/javascript'>
		window.onload=function()
		{
			var img    = new Image;
			img.src    = '%s.jpg';
			img.onload = function () 
			{
				var ctx = document.getElementById('motion').getContext('2d');
				ctx.strokeStyle = "red";
				ctx.drawImage(img, 0, 0, motion.width, motion.height);
				%s
			}
		}
		</script>
		<canvas id="motion" width="%d" height="%d"></canvas>"""
		shapes = b""
		for shape in self.comparison["shapes"]:
			shapes += b"ctx.strokeRect(%d, %d, %d, %d);\n"%(shape["x"]+1,shape["y"]+1,shape["width"]-2,shape["height"]-2)
		return html%(useful.tobytes(self.getFilename()), shapes, self.comparison["geometry"]["width"], self.comparison["geometry"]["height"])

	def getInformations(self):
		""" Return the informations of motion """
		result    = self.comparison.copy()
		result["image"]    = self.getFilename() + ".jpg"
		result["path"]     = self.path
		result["index"]    = self.index
		result["date"]     = self.date
		result["motionId"] = self.motionId
		return result

	async def save(self):
		""" Save the image on sd card """
		await historic.Historic.addMotion(useful.tostrings(self.path), self.getFilename(), self.motion.getImage(), self.getInformations(), self.getHtmlShapes())

	def compare(self, previous, set=False):
		""" Compare two motion images to get differences """
		self.motion.setErrorLight     (self.config.lightErrorRange)
		self.motion.setErrorSaturation(self.config.saturationErrorRange)
		self.motion.setErrorHue       (self.config.hueErrorRange)
		res = self.motion.compare(previous.motion)
		if set:
			self.comparison = res
		return res

	def getMotionDetected(self):
		""" Get the motion detection status """
		return self.motionDetected
	
	def setMotionDetected(self):
		""" Set the motion detection status """
		self.motionDetected = True
	
	def get(self):
		""" Get the image captured """
		return self.motion.getImage()
	
	def getComparison(self):
		""" Return the comparison result """
		return self.comparison

	def getDiffCount(self):
		""" Get the difference contigous """
		if self.comparison:
			return self.comparison["diff"]["count"]
		return 0

	def resetDifferences(self):
		""" Reset the differences, used during the camera stabilization image """
		self.comparison = None

class Motion:
	""" Class to manage the motion capture """
	def __init__(self, config= None, onBattery=False, pirDetection=False):
		self.images = []
		self.index  = 0
		self.config = config
		self.onBattery = onBattery
		self.pirDetection = pirDetection

	def open(self):
		""" Open camera """
		video.Camera.open()
		self.resume()

	def resume(self):
		""" Resume the camera, restore the camera configuration after an interruption """
		# video.Camera.framesize(b"UXGA") # 1600x1200
		# video.Camera.framesize(b"SXGA") # 1280x1024
		# video.Camera.framesize(b"XGA")  # 1024x768
		video.Camera.framesize(b"SVGA") # 800x600
		video.Camera.pixformat(b"JPEG")
		video.Camera.quality(10)
		video.Camera.brightness(0)
		video.Camera.contrast(0)
		video.Camera.saturation(0)
		video.Camera.hmirror(0)
		video.Camera.vflip(0)

		detected, changePolling = self.detect(False)
		if detected == False:
			self.images = []

	async def capture(self):
		""" Capture motion image """
		result = None
		retry = 10
		if len(self.images) >= self.config.maxMotionImages:
			image = self.images.pop()
			
			# If motion detected on image, on battery the first five images are sent
			if image.getMotionDetected() or (self.onBattery and self.pirDetection and image.index <= 3):
				# Notification of motion
				result = ("Motion %s.jpg"%image.getFilename(), image)

				# Save image to sdcard
				await image.save()
			else:
				image.deinit()
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
		""" Indicates if the camera is stabilized """
		# If the PIR detection force the stabilization
		if self.pirDetection == True:
			stabilized = True
		# If the camera not stabilized
		elif len(self.images) < self.config.stabilizationCamera:
			stabilized = False
		else:
			stabilized = True
		return stabilized

	def isDetected(self, comparison):
		""" Indicates if motion detected """
		if comparison:
			# If image seem not equal to previous
			if comparison["diff"]["count"] > self.config.contigousDetection:
				return True
		return False

	def compare(self, display=True):
		""" Compare all images captured and search differences """
		differences = {}
		if len(self.images) >= 2:
			current = self.images[0]
			
			# Compute the motion identifier
			for previous in self.images[1:]:
				comparison = current.compare(previous, True)

				# If camera not stabilized
				if self.isStabilized() == False:
					# Reject the differences
					current.resetDifferences()
					break

				# If image seem equal to previous
				if not self.isDetected(comparison):
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
					diffs += " %d:%d"%(image.getMotionId(), image.getDiffCount())
			if display:
				sys.stdout.write("\r%s %s    "%(useful.dateToString()[12:], diffs))
		return differences

	def detect(self, display=True):
		""" Detect motion """
		detected = False
		changePolling = False

		# Compute the list of differences
		differences = self.compare(display)

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
					# Glitch ignored
					detected = False
					break
		# Not detected
		else:
			detected = False

		if detected:
			# Mark all motion images
			for image in self.images:
				# If image seem not equal to previous
				if self.isDetected(image.getComparison()):
					image.setMotionDetected()
		return detected, changePolling

async def sleep_ms(duration):
	""" Multiplatform sleep_ms """
	await uasyncio.sleep_ms(duration)

async def detectMotion(onBattery, pirDetection):
	""" Asynchronous motion detection main routine """
	from server   import notifyMessage
	from motion   import MotionConfig
	import wifi

	# Open motion configuration
	motionConfig      = MotionConfig()
	if motionConfig.load() == False:
		motionConfig.save()

	motion = None
	pollingCounter = 0
	previousReserved = None
	pollingFrequency = 100
	batteryLevel = -2
	if onBattery:
		if pirDetection == True:
			pollingFrequency = 3
		motionConfig.load()
		wifiOn = False
		startTime = time.time()
	else:
		wifiOn = True
	detection = None

	previousActivated = None
	reservedCount = 0
	waitAfterUnreserve = 0
	
	while True:
		await server.waitResume()
  
		# If detection
		if detection != None:
			message, image = detection
			# Release image buffer
			image.deinit()

		if motionConfig.activated:
			activated = False
			if motionConfig.suspendOnPresence:
				if presence.isPresenceDetected() == False:
					activated = True
			else:
				activated = True
		else:
			activated = False

		if previousActivated != activated:
			await notifyMessage(b"Motion detection %s" %(b"activated" if activated else b"stopped"))
			previousActivated = activated

		# If the motion activated
		if activated:
			# If motion not initialized
			if motion == None:
				# The sdcard not available on battery
				if onBattery != True:
					await historic.Historic.getRoot()
				motion = Motion(motionConfig, onBattery, pirDetection)
				motion.open()
				await sleep_ms(3000)

			# If camera available to detect motion
			if video.Camera.isReserved() == False:
				if waitAfterUnreserve > 0:
					waitAfterUnreserve -= 1
					#print("Waiting before restart %d"%waitAfterUnreserve)
					await sleep_ms(500)
				else:
					waitAfterUnreserve = 0
					reservedCount = 0
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
							detection = await motion.capture()

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
								await notifyMessage(message, image.get())
							# Detect motion
							detected, changePolling = motion.detect()

							# If motion found
							if changePolling == True:
								# Speed up the polling frequency
								pollingFrequency = 15
								historic.Historic.setMotionState(True)
								startTime = time.time()
							else:
								# Slow down the polling frequency
								pollingFrequency = 200
								historic.Historic.setMotionState(False)
					except Exception as err:
						print(useful.exception(err))
			else:
				# Camera buzy, motion capture suspended
				previousReserved = True
				reservedCount += 1
				if reservedCount > 6:
					await notifyMessage(b"Motion detection suspended during web browsing")
					reservedCount = 0
				await sleep_ms(10000)
				waitAfterUnreserve = 20
		else:
			# Motion capture disabled
			await sleep_ms(500)
		pollingCounter += 1

		# Reload configuration each 3 s
		if pollingCounter % 5 == 0:
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


