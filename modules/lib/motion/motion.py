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
from gc import collect
from motion import presence,historic

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

		# Error range ignore light modification (5% of 256)
		self.lightErrorRange=13

		# Max images in motion historic
		self.maxMotionImages=10

		# Glitch threshold of image ignored (sometime the camera bug)
		self.thresholdGlitch=2

		# Threshold of minimum image to detect motion
		self.thresholdMotion=3

		# Number of images before camera stabilization
		self.stabilizationCamera=8

		# Notify motion
		self.notify = True

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
	created = [0]
	def __init__(self, motion, config):
		self.motion = motion
		self.baseIndex[0] += 1
		self.created[0] += 1
		self.index    = self.baseIndex[0]
		self.filename = None
		self.motionId = None
		self.date     = useful.dateToString()
		self.filename = useful.dateToFilename()
		self.path     = useful.dateToPath()[:-1] + b"0"
		self.motionDetected = False
		self.config = config
		self.comparison = None

	def deinit(self):
		""" Destructor """
		self.created[0] -= 1
		if self.created[0] >= 12:
			print("Destroy %d"%self.created[0])
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
		return "%s Id=%d D=%d"%(self.filename, self.index, self.getDiffCount())

	def getMessage(self):
		""" Get the message of motion """
		return "%s Id=%d D=%d"%(self.date, self.index, self.getDiffCount())

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
			shapes += b"				ctx.strokeRect(%d, %d, %d, %d);\n"%(shape["x"]+1,shape["y"]+1,shape["width"]-2,shape["height"]-2)
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

	def compare(self, previous, set=False, extractShape=True):
		""" Compare two motion images to get differences """
		res = self.motion.compare(previous.motion, {"errorLight":self.config.lightErrorRange, "extractShape":extractShape})
		if set or self.comparison == None:
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

	def getDiffHisto(self):
		""" Get the histogram difference """
		if self.comparison:
			return self.comparison["diff"]["histo"]
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
		self.imageBackground = None

	def __del__(self):
		""" Destructor """
		self.cleanup()

	def cleanup(self):
		""" Clean up all images """
		for image in self.images:
			if id(image) != id(self.imageBackground):
				image.deinit()
		self.images = []
		if self.imageBackground:
			self.imageBackground.deinit()
		self.imageBackground = None

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
			self.cleanup()

	async def capture(self):
		""" Capture motion image """
		result = None
		# If enough image taken
		if len(self.images) >= self.config.maxMotionImages:
			# Get older image
			image = self.images.pop()
			
			# If motion detected on image, on battery the first five images are sent
			if image.getMotionDetected() or (self.onBattery and self.pirDetection and image.index <= 3):
				# Notification of motion
				result = (image.getMessage(), image)

				# Save image to sdcard
				await image.save()
			else:
				# Destroy image
				self.deinitImage(image)

		image = ImageMotion(video.Camera.motion(), self.config)
		self.images.insert(0, image)
		self.index += 1
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
			for previous in self.images[1:5]:
				# # If image not already compared
				comparison = current.compare(previous, False, False)
				# print("D%d H%d id%d idx%d"%(comparison["diff"]["count"], comparison["diff"]["histo"], previous.getMotionId() if previous.getMotionId() else -1, previous.index))
	
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

				# Compare the image with the background if existing and extract modification
				if self.imageBackground != None:
					comparison = current.compare(self.imageBackground, True, True)

			# Compute the list of differences
			diffs = ""
			for image in self.images:
				differences.setdefault(image.getMotionId(), []).append(image.getMotionId())
				if image.getMotionId() != None:
					diffs += " %d:%d%s"%(image.getMotionId(), image.getDiffCount(), chr(0x41 + ((256-image.getDiffHisto())//10)))
			if display:
				sys.stdout.write("\r%s %s    "%(useful.dateToString()[12:], diffs))
		return differences

	def deinitImage(self, image):
		""" Release image allocated """
		if image:
			if not image in self.images:
				if image != self.imageBackground:
					image.deinit()

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
			image = self.imageBackground
			self.imageBackground = self.images[0]
			self.deinitImage(image)
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
			motion.deinitImage(image)

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
			if motionConfig.notify:
				await notifyMessage(b"motion detection %s" %(b"on" if activated else b"off"))
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
									message += " Bat=%s%%"%batteryLevel
								if motionConfig.notify:
									await notifyMessage(message, image.get())
							# Detect motion
							detected, changePolling = motion.detect()

							# If motion found
							if changePolling == True:
								# Speed up the polling frequency
								pollingFrequency = 10
								historic.Historic.setMotionState(True)
								startTime = time.time()
							else:
								# Slow down the polling frequency
								pollingFrequency = 50
								historic.Historic.setMotionState(False)
					except Exception as err:
						print(useful.exception(err))
			else:
				# Camera buzy, motion capture suspended
				previousReserved = True
				reservedCount += 1
				if reservedCount > 6:
					if motionConfig.notify:
						await notifyMessage(b"motion detection suspended")
					reservedCount = 0
				await sleep_ms(10000)
				waitAfterUnreserve = 20
		else:
			# Motion capture disabled
			await sleep_ms(500)
		pollingCounter += 1

		if motion.index %20 == 0:
			collect()

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


