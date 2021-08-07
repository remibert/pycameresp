# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Motion detection only work with ESP32CAM (Requires specially modified ESP32CAM firmware to handle motion detection.) """
import sys
import uasyncio
import video
from gc import collect
from tools import useful, jsonconfig, battery
from server.notifier import Notifier
from server.server   import Server
from server.presence import Presence
from motion.historic import Historic

class MotionConfig(jsonconfig.JsonConfig):
	""" Configuration class of motion detection """
	def __init__(self):
		jsonconfig.JsonConfig.__init__(self)
		# Indicates if the motion is activated
		self.activated = False

		# Suspend the motion detection when presence detected
		self.suspendOnPresence = True

		# Minimum difference contigous threshold to detect movement
		self.differencesDetection = 4

		# Error range ignore light modification (% of 256)
		self.lightErrorRange=12

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

		# Empty mask is equal disable masking
		self.mask = b""

class ImageMotion:
	""" Class managing a motion detection image """
	baseIndex = [0]
	motionBaseId = [0]
	created = [0]
	def __init__(self, motion, config):
		""" Constructor """
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
		if self.created[0] >= 32:
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
		return await Historic.addMotion(useful.tostrings(self.path), self.getFilename(), self.motion.getImage(), self.getInformations(), self.getHtmlShapes())

	def compare(self, previous, extractShape=True):
		""" Compare two motion images to get differences """
		res = self.motion.compare(previous.motion, extractShape)
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

	def getSize(self):
		""" Return the size of image buffer """
		return self.motion.getSize()

	def refreshConfig(self):
		""" Refresh the motion detection configuration """
		if self.motion != None:
			mask = useful.tobytes(self.config.mask)
			if not b"/" in mask:
				mask = b""
			errorLight = self.config.lightErrorRange
			self.motion.configure({"mask":mask, "errorLights":[[0,1],[2*errorLight,errorLight//2],[3*errorLight, errorLight],[256,errorLight]]})

class SnapConfig:
	""" Store last motion information """
	info = None

	@staticmethod
	def get(width=None, height=None):
		""" Get the last motion information """
		if width != None and height != None:
			SnapConfig.info = SnapConfig(width, height)
		elif SnapConfig.info == None:
			SnapConfig.info = SnapConfig()
		return SnapConfig.info

	def __init__(self, width=800, height=600):
		""" Constructor """
		self.width  = width
		self.height = height
		if (((self.width/8) % 8) == 0):
			self.square_x = 64
		else:
			self.square_x = 40

		if (((self.height/8) % 8) == 0):
			self.square_y = 64
		else:
			self.square_y = 40
		self.diff_x = self.width  // self.square_x
		self.diff_y = self.height // self.square_y
		self.max = self.diff_x * self.diff_y

class Motion:
	""" Class to manage the motion capture """
	def __init__(self, config= None, pirDetection=False):
		self.images = []
		self.index  = 0
		self.config = config
		self.pirDetection = pirDetection
		self.imageBackground = None
		self.mustRefreshConfig = True
		self.quality = 15
		self.previousQuality = 0

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
			return True
		else:
			return False

	def resume(self):
		""" Resume the camera, restore the camera configuration after an interruption """
		video.Camera.framesize(b"%dx%d"%(SnapConfig.get().width, SnapConfig.get().height))
		video.Camera.pixformat(b"JPEG")
		video.Camera.quality(self.quality)
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
			if image.getMotionDetected() or (self.pirDetection and image.index <= 3):
				# Notification of motion
				result = (image.getMessage(), image)

				# Save image to sdcard
				if await image.save() == False:
					if self.config.notify:
						await Notifier.notify("Failed to save on sd card")
			else:
				# Destroy image
				self.deinitImage(image)

		image = ImageMotion(video.Camera.motion(), self.config)
		if self.mustRefreshConfig:
			image.refreshConfig()
			self.mustRefreshConfig = False
		self.images.insert(0, image)
		self.index += 1
		return result

	def refreshConfig(self):
		""" Force the refresh of motion configuration """
		self.mustRefreshConfig = True

	def isStabilized(self):
		""" Indicates if the camera is stabilized """
		# If the PIR detection force the stabilization
		if self.pirDetection == True:
			stabilized = True
		# If the camera not stabilized
		elif len(self.images) < self.config.stabilizationCamera and len(self.images) < self.config.maxMotionImages:
			stabilized = False
		else:
			stabilized = True
		return stabilized

	def isDetected(self, comparison):
		""" Indicates if motion detected """
		if comparison:
			# If image seem not equal to previous
			if comparison["diff"]["count"] >= self.config.differencesDetection:
				return True
		return False

	def adjustQuality(self, current):
		""" Adjust the image quality according to the size of image to"""
		if len(self.images) >= self.config.maxMotionImages:
			changed = False
			size = current.getSize()
			if size > 62*1024:
				if self.quality < 63:
					self.quality += 1
					changed = True
					video.Camera.quality(self.quality, False)
			else:
				if self.quality >= 1:
					if size < 50*1024:
						self.quality -= 1
						changed = True
						video.Camera.quality(self.quality, False)
			if changed == False:
				if self.previousQuality != self.quality:
					useful.logError("Adjust image quality from %d to %d"%(self.previousQuality, self.quality))
					self.previousQuality = self.quality

	def compare(self, display=True):
		""" Compare all images captured and search differences """
		differences = {}
		if len(self.images) >= 2:
			current = self.images[0]
			
			self.adjustQuality(current)

			# Compute the motion identifier
			for previous in self.images[1:]:
				# # If image not already compared
				comparison = current.compare(previous, False)
	
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
					comparison = current.compare(self.imageBackground, True)

			# Compute the list of differences
			diffs = ""
			index = 0
			for image in self.images:
				differences.setdefault(image.getMotionId(), []).append(image.getMotionId())
				if image.getMotionId() != None:
					if image.index % 10 == 0:
						trace = "_"
					else:
						trace = " "
					if image.index > index:
						index = image.index
					diffs += "%d:%d%s%s"%(image.getMotionId(), image.getDiffCount(), chr(0x41 + ((256-image.getDiffHisto())//10)), trace)
			if display:
				sys.stdout.write("\r%s %s (%d) "%(useful.dateToString()[12:], diffs, index))
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
	def __init__(self, pirDetection):
		""" Constructor """
		self.pirDetection = pirDetection
		self.loadConfig()
		self.motion = None
		
		self.batteryLevel = -2
		if self.pirDetection == True:
			self.pollingFrequency = 3
		else:
			self.pollingFrequency = 100
		self.detection = None
		self.activated = None

	def loadConfig(self):
		""" Load motion configuration """
		# Open motion configuration
		self.motionConfig      = MotionConfig()
		if self.motionConfig.load() == False:
			self.motionConfig.save()
		self.batteryConfig = battery.BatteryConfig()
		if self.batteryConfig.load() == False:
			self.batteryConfig.save()

	def refreshConfig(self):
		""" Refresh the configuration : it can be changed by web page """
		# If configuration changed
		if self.motionConfig.isChanged():
			self.motionConfig.load()
			useful.logError("Change motion config %s"%self.motionConfig.toString(), display=False)
			if self.motion:
				self.motion.refreshConfig()
	async def run(self):
		""" Main asynchronous task """
		await useful.taskMonitoring(self.detect)

	def inactivityTimeout(self, timer):
		""" Inactivity timeout """
		useful.reboot("Automatic reboot after inactivity in motion")
	
	async def detect(self):
		""" Detect motion """
		result = False
		# Wait the server resume
		await Server.waitResume()

		# Release previously alocated image
		self.releaseImage()

		# If the motion detection activated
		if await self.isActivated():
			# Capture motion
			result = await self.capture()
		else:
			await uasyncio.sleep(3)
			result = True

		# Refresh configuration when it changed
		self.refreshConfig()

		return result

	async def isActivated(self):
		""" Indicates if the motion detection is activated according to configuration or presence """
		result = False
		if self.motionConfig.activated:
			if self.motionConfig.suspendOnPresence:
				if Presence.isDetected() == False:
					result = True
			else:
				result = True
			
		if self.activated != result:
			if self.motionConfig.notify:
				await Notifier.notify(b"Motion detection %s" %(b"on" if result else b"off"))
			self.activated = result
		if result == False:
			# Motion capture disabled
			await uasyncio.sleep_ms(500)
		return result

	async def initMotion(self):
		""" Initialize motion detection """
		firstInit = False

		# If motion not initialized
		if self.motion == None:
			self.motion = Motion(self.motionConfig, self.pirDetection)
			if self.motion.open() == False:
				self.motion = None
				raise Exception("Cannot open camera")
			else:
				firstInit = True

		# If the camera configuration changed
		if video.Camera.isModified() or firstInit:
			# Restore motion configuration
			self.motion.resume()
			video.Camera.clearModified()

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
		if self.motion and self.motion.isStabilized() == True:
			await uasyncio.sleep_ms(self.pollingFrequency)

		try:
			# Waits for the camera's availability
			reserved = await video.Camera.reserve(self, timeout=60)

			# If reserved
			if reserved:
				# Initialize motion detection
				await self.initMotion()

				# Capture motion image
				self.detection = await self.motion.capture()

				# If motion detected
				if self.detection != None:
					# Notify motion with push over
					message, image = self.detection
					if self.motionConfig.notify:
						await Notifier.notify(message, image.get())
				# Detect motion
				detected, changePolling = self.motion.detect()

				# If motion found
				if changePolling == True:
					# Speed up the polling frequency
					self.pollingFrequency = 10
					Historic.setMotionState(True)
				else:
					# Slow down the polling frequency
					self.pollingFrequency = 50
					Historic.setMotionState(False)
				result = True
			else:
				if self.motionConfig.notify:await Notifier.notify(b"Motion detection suspended")
				result = True

		finally:
			if reserved:
				await video.Camera.unreserve(self)
		return result

async def detectMotion(pirDetection):
	""" Asynchronous motion detection main routine """
	detection = Detection(pirDetection)
	await detection.run()

