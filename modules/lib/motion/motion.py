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
from server   import notifyMessage

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

		# Error range ignore light modification (10% of 256)
		self.lightErrorRange=24

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

class MaskingConfig:
	""" Configuration class of zone masking for hide area in motion detection """
	def __init__(self):
		# Indicates if the motion is activated
		self.activated = False

		# Empty mask is equal disable masking
		self.masking = ""


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
		if self.motion:
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
			MotionInfo.set(res)
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

class MotionInfo:
	""" Store last motion information """
	motion = [{
			'diff': 
			{
				'count': 0, 
				'max': 300, 
				'light': 94,
				'squarex':40,
				'squarey':40,
				'width':20,
				'height':15
			}, 
			'geometry': 
			{
				'height': 600, 'width': 800
			}
		}]

	@staticmethod
	def get():
		""" Get the last motion information """
		return MotionInfo.motion[0]

	@staticmethod
	def set(motion):
		""" Set the last motion information """
		MotionInfo.motion[0] = motion

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
		if video.Camera.open():
			self.resume()
			return True
		else:
			return False

	def resume(self):
		""" Resume the camera, restore the camera configuration after an interruption """
		# video.Camera.framesize(b"1600x1200") # 1600x1200
		# video.Camera.framesize(b"1280x1024") # 1280x1024
		# video.Camera.framesize(b"1024x768")  # 1024x768
		video.Camera.framesize(b"800x600") # 800x600
		video.Camera.pixformat(b"JPEG")
		video.Camera.quality(15)
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
			for previous in self.images[1:]:
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
					if image.index % 10 == 0:
						trace = "_"
					else:
						trace = " "
					diffs += "%d:%d%s%s"%(image.getMotionId(), image.getDiffCount(), chr(0x41 + ((256-image.getDiffHisto())//10)), trace)
			if display:
				sys.stdout.write("\r%s %s  "%(useful.dateToString()[12:], diffs))
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

class Detection:
	""" Asynchronous motion detection object """
	def __init__(self, onBattery, pirDetection):
		""" Constructor """
		import wifi

		self.onBattery = onBattery
		self.pirDetection = pirDetection
		self.loadConfig()
		self.motion = None
		self.pollingConfig = 0
		self.pollingFrequency = 100
		self.batteryLevel = -2
		if self.onBattery:
			if self.pirDetection == True:
				self.pollingFrequency = 3
			self.wifiOn = False
			self.startTime = time.time()
		else:
			self.wifiOn = True
		self.detection = None
		self.activated = None

	def loadConfig(self):
		""" Load motion configuration """
		# Open motion configuration
		self.motionConfig      = MotionConfig()
		if self.motionConfig.load() == False:
			self.motionConfig.save()

	def refreshConfig(self):
		""" Refresh the configuration : it can be changed by web page """
		self.pollingConfig += 1

		# Reload configuration each 3 s
		if self.pollingConfig % 5 == 0:
			self.motionConfig.load()

	async def run(self):
		""" Main asynchronous task """
		await useful.taskMonitoring(self.detect)
	
	async def detect(self):
		""" Detect motion """
		result = False
		# Wait the server resume
		await server.waitResume()

		# Release previously alocated image
		self.releaseImage()

		# If the motion detection activated
		if await self.isActivated():
			# Initialize motion detection
			await self.initMotion()

			# Capture motion
			result = await self.capture()
		else:
			result = True

		# Refresh configuration when it changed
		self.refreshConfig()

		# Deep sleep on battery
		self.deepsleep()
		return result

	async def isActivated(self):
		""" Indicates if the motion detection is activated according to configuration or presence """
		result = False
		if self.motionConfig.activated:
			if self.motionConfig.suspendOnPresence:
				if presence.Presence.isDetected() == False:
					result = True
			else:
				result = True
			
		if self.activated != result:
			if self.motionConfig.notify:
				await notifyMessage(b"motion detection %s" %(b"on" if result else b"off"))
			self.activated = result
		if result == False:
			# Motion capture disabled
			await uasyncio.sleep_ms(500)
		return result

	async def initMotion(self):
		""" Initialize motion detection """
		# If motion not initialized
		if self.motion == None:
			# The sdcard not available on battery
			if self.onBattery != True:
				await historic.Historic.getRoot()
			self.motion = Motion(self.motionConfig, self.onBattery, self.pirDetection)
			if self.motion.open() == False:
				self.motion = None
				raise Exception("Cannot open camera")

	def releaseImage(self):
		""" Release motion image allocated """
		# If detection
		if self.detection:
			message, image = self.detection
			# Release image buffer
			self.motion.deinitImage(image)

		# Force garbage collection each 20 images
		if self.motion:
			if self.motion.index %30 == 0:
				collect()

	async def capture(self):
		""" Capture motion """
		result = False
		# If camera not stabilized speed start
		if self.motion.isStabilized() == True:
			await uasyncio.sleep_ms(self.pollingFrequency)

		try:
			# Waits for the camera's availability
			reserved = await video.Camera.reserve(self, timeout=60)

			# If reserved
			if reserved:
				# If the camera configuration changed
				if video.Camera.isModified():
					# Restore motion configuration
					self.motion.resume()
					video.Camera.clearModified()

				# Capture motion image
				self.detection = await self.motion.capture()

				# If motion detected
				if self.detection != None:
					# Notify motion with push over
					message, image = self.detection
					# On battery the wifi start after taking pictures
					if self.wifiOn == False:
						from server import start
						from tools import Battery
						start(withoutServer=True)
						self.wifiOn = True
						self.batteryLevel = Battery.getLevel()
					if self.batteryLevel >= 0:
						message += " Bat=%s%%"%batteryLevel
					if self.motionConfig.notify:
						await notifyMessage(message, image.get())
				# Detect motion
				detected, changePolling = self.motion.detect()

				# If motion found
				if changePolling == True:
					# Speed up the polling frequency
					self.pollingFrequency = 10
					historic.Historic.setMotionState(True)
					self.startTime = time.time()
				else:
					# Slow down the polling frequency
					self.pollingFrequency = 50
					historic.Historic.setMotionState(False)
				result = True
			else:
				await notifyMessage(b"motion detection suspended")
				result = True

		finally:
			if reserved:
				await video.Camera.unreserve(self)
		return result
	
	def deepsleep(self):
		""" Post treatment for detection and force deep sleep on battery """
		# If the battery mode activated
		if self.onBattery:
			# If the motion detection activated
			if self.motionConfig.activated:
				# Wait duration after the last detection
				if time.time() > self.startTime + self.motionConfig.awakeTime:
					import machine
					print("")
					print("####################################")
					print("# DEEP SLEEP TO WAIT PIR DETECTION #")
					print("####################################")
					machine.deepsleep(10000)

async def detectMotion(onBattery, pirDetection):
	""" Asynchronous motion detection main routine """
	detection = Detection(onBattery, pirDetection)
	await detection.run()

