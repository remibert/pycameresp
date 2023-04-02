# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Motion detection only work with ESP32CAM (Requires specially modified ESP32CAM firmware to handle motion detection.) """
from gc import collect
import sys
import time
import uasyncio
import video
from server.notifier import Notifier
from server.presence import Presence
from server.webhook  import WebhookConfig
from motion.historic import Historic
from video.video     import Camera
from tools import logger,jsonconfig,lang,linearfunction,tasking,strings,filesystem,date,topic

STATE_DURATION = 30
class MotionConfig(jsonconfig.JsonConfig):
	""" Configuration class of motion detection """
	def __init__(self):
		jsonconfig.JsonConfig.__init__(self)
		# Indicates if the motion is activated
		self.activated = False

		# Suspend the motion detection when presence detected
		self.suspend_on_presence = True

		# Minimum difference contigous threshold to detect movement
		self.differences_detection = 4

		# Sensitivity in percent (100% = max sensitivity, 0% = min sensitivity)
		self.sensitivity=80

		# Max images in motion historic
		self.max_motion_images=10

		# Glitch threshold of image ignored (sometime the camera bug)
		self.threshold_glitch=2

		# Threshold of minimum image to detect motion
		self.threshold_motion=3

		# Number of images before camera stabilization
		self.stabilization_camera=8

		# Turn on the led flash when the light goes down
		self.light_compensation = False

		# Notify motion detection or problem to save on sd card
		self.notify = True

		# Notify motion state change
		self.notify_state = False

		# Permanent detection without notification.
		# To keep all motion detection in the presence of occupants
		self.permanent_detection = False

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
		self.motion_id = None
		self.date     = date.date_to_string()
		self.filename = date.date_to_filename()
		path = date.date_to_path()
		if path[-1] in [0x30,0x31,0x32,0x33,0x34]:
			path = path[:-1] + b"0"
		else:
			path = path[:-1] + b"5"
		self.path     = path
		self.motion_detected = False
		self.config = config
		self.comparison = None

	def deinit(self):
		""" Destructor """
		self.created[0] -= 1
		if self.created[0] >= 32:
			print("Destroy %d"%self.created[0])
		if self.motion:
			self.motion.deinit()

	def set_motion_id(self, motion_id = None):
		""" Set the unique image identifier """
		if motion_id is None:
			self.motionBaseId[0] += 1
			self.motion_id = self.motionBaseId[0]
		else:
			if self.motion_id is None:
				self.motion_id = motion_id
			else:
				print("Motion id already set")

	def get_motion_id(self):
		""" Get the unique image identifier """
		return self.motion_id

	def get_filename(self):
		""" Get the storage filename """
		return "%s Id=%d D=%d"%(self.filename, self.index, self.get_diff_count())

	def get_message(self):
		""" Get the message of motion """
		return "%s %s D=%d"%(strings.tostrings(lang.motion_detected), self.date[-8:], self.get_diff_count())

	def get_informations(self):
		""" Return the informations of motion """
		if self.comparison is not None:
			result    = self.comparison.copy()
		else:
			result = {}
		result["image"]    = self.get_filename() + ".jpg"
		result["path"]     = self.path
		result["index"]    = self.index
		result["date"]     = self.date
		result["motion_id"] = self.motion_id
		return result

	async def save(self):
		""" Save the image on sd card """
		return await Historic.add_motion(strings.tostrings(self.path), self.get_filename(), self.motion.get_image(), self.get_informations())

	def compare(self, previous):
		""" Compare two motion images to get differences """
		res = self.motion.compare(previous.motion)
		self.comparison = res
		return res

	def get_motion_detected(self):
		""" Get the motion detection status """
		return self.motion_detected

	def set_motion_detected(self):
		""" Set the motion detection status """
		self.motion_detected = True

	def get(self):
		""" Get the image captured """
		return self.motion.get_image()

	def get_comparison(self):
		""" Return the comparison result """
		return self.comparison

	def get_diff_count(self):
		""" Get the difference contigous """
		if self.comparison:
			return self.comparison["diff"]["count"]
		return 0

	def get_diff_histo(self):
		""" Get the histogram difference """
		if self.comparison:
			return self.comparison["diff"]["diffhisto"]
		return 0

	def get_differences(self):
		""" Get the differences """
		if self.comparison:
			return self.comparison["diff"]["diffs"]
		return ""

	def reset_differences(self):
		""" Reset the differences, used during the camera stabilization image """
		self.comparison = None

	def get_size(self):
		""" Return the size of image buffer """
		return self.motion.get_size()

	def refresh_config(self):
		""" Refresh the motion detection configuration """
		if self.motion is not None:
			mask = strings.tobytes(self.config.mask)
			if not b"/" in mask:
				mask = b""
			errorLight = linearfunction.get_fx(self.config.sensitivity, linearfunction.get_linear(100,8,0,64))
			self.motion.configure(\
				{
					"mask":mask,
					"errorLights":[[0,10],[30,10],[128,errorLight],[256,errorLight]],
					"errorHistos":[[0,0],[32,32],[128,128],[256,256]]
				})

class SnapConfig:
	""" Store last motion information """
	info = None

	@staticmethod
	def get(width=None, height=None):
		""" Get the last motion information """
		if width is not None and height is not None:
			SnapConfig.info = SnapConfig(width, height)
		elif SnapConfig.info is None:
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

class MotionCore:
	""" Class to manage the motion capture """
	def __init__(self, config= None, pir_detection=False):
		self.images = []
		self.index  = 0
		self.config = config
		self.pir_detection = pir_detection
		self.image_background = None
		self.must_refresh_config = True
		self.quality = 15
		self.previous_quality = 0
		self.flash_level = 0

	def __del__(self):
		""" Destructor """
		self.cleanup()

	def cleanup(self):
		""" Clean up all images """
		for image in self.images:
			if id(image) != id(self.image_background):
				image.deinit()
		self.images = []
		if self.image_background:
			self.image_background.deinit()
		self.image_background = None

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
		video.Camera.flash(self.flash_level)

		detected, change_polling = self.detect(False)
		if detected is False:
			self.cleanup()

	def manage_flash(self, motion):
		""" Manage the flash level is low light """
		# Light can be compensed with flash led
		if self.config.light_compensation:
			# If it has enough light
			if motion.get_light() >= 50:
				# If flash led working
				if self.flash_level > 8:
					# Reduce light of flash led
					self.flash_level -= 2
					video.Camera.flash(self.flash_level)
			# If it has not enough light
			elif motion.get_light() <= 40:
				# If flash to low
				if self.flash_level <= 192:
					# Increase the light of flash led
					self.flash_level += 2
					video.Camera.flash(self.flash_level)
			# If low level for flash
			if self.flash_level < 8:
				# Show motion started indicator
				self.flash_level = 8
				video.Camera.flash(self.flash_level)
		else:
			self.stop_light()

	async def capture(self):
		""" Capture motion image """
		result = None
		# If enough image taken
		if len(self.images) >= self.config.max_motion_images:
			# Get older image
			image = self.images.pop()

			# If motion detected on image, on battery the first five images are sent
			if image.get_motion_detected() or (self.pir_detection and image.index <= 3):
				# Notification of motion
				result = (image.get_message(), image)

				# Save image to sdcard
				if await image.save() is False:
					Notifier.notify(topic=topic.information, message=lang.failed_to_save, enabled=self.config.notify)
			else:
				# Destroy image
				self.deinit_image(image)

		motion = video.Camera.motion()
		self.manage_flash(motion)
		image = ImageMotion(motion, self.config)
		if self.must_refresh_config:
			image.refresh_config()
			self.must_refresh_config = False
		self.images.insert(0, image)
		self.index += 1
		return result

	def stop_light(self):
		""" Stop the light """
		# If flash led working and compensation disabled
		if self.flash_level > 0:
			# Stop flash led
			self.flash_level = 0
			video.Camera.flash(self.flash_level)

	def refresh_config(self):
		""" Force the refresh of motion configuration """
		self.must_refresh_config = True

	def is_stabilized(self):
		""" Indicates if the camera is stabilized """
		# If the PIR detection force the stabilization
		if self.pir_detection is True:
			stabilized = True
		# If the camera not stabilized
		elif len(self.images) < self.config.stabilization_camera and len(self.images) < self.config.max_motion_images:
			stabilized = False
		else:
			stabilized = True
		return stabilized

	def is_detected(self, comparison):
		""" Indicates if motion detected """
		if comparison:
			# If image seem not equal to previous
			if comparison["diff"]["count"] >= self.config.differences_detection:
				return True
		return False

	def adjust_quality(self, current):
		""" Adjust the image quality according to the size of image (the max possible is 64K) """
		if len(self.images) >= self.config.max_motion_images:
			changed = False
			size = current.get_size()
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
			if changed is False:
				if self.previous_quality != self.quality:
					self.previous_quality = self.quality

	def compare(self, display=True):
		""" Compare all images captured and search differences """
		differences = {}
		if len(self.images) >= 2:
			current = self.images[0]

			self.adjust_quality(current)

			# Compute the motion identifier
			for previous in self.images[1:]:
				# # If image not already compared
				comparison = current.compare(previous)

				# If camera not stabilized
				if self.is_stabilized() is False:
					# Reject the differences
					current.reset_differences()
					break

				# If image is too dark
				if current.motion.get_light() <= 20:
					# Reuse the motion identifier
					current.set_motion_id(previous.motion_id)
					break

				# If image seem equal to previous
				if not self.is_detected(comparison):
					# Reuse the motion identifier
					current.set_motion_id(previous.motion_id)
					break
			else:
				# Create new motion id
				current.set_motion_id()

				# Compare the image with the background if existing and extract modification
				if self.image_background is not None:
					comparison = current.compare(self.image_background)

			# Compute the list of differences
			diffs = b""
			index = 0
			mean_light = -1
			for image in self.images:
				if mean_light == -1:
					mean_light = image.motion.get_light()
				differences.setdefault(image.get_motion_id(), []).append(image.get_motion_id())
				if image.get_motion_id() is not None:
					if image.index % 10 == 0:
						trace = b"_"
					else:
						trace = b" "
					if image.index > index:
						index = image.index
					diffs += b"%d:%d%s%s"%(image.get_motion_id(), image.get_diff_count(), (0x41 + ((256-image.get_diff_histo())//10)).to_bytes(1, 'big'), trace)
			if display:
				line = b"\r%s %s L%d (%d) "%(date.time_to_html(seconds=True), bytes(diffs), mean_light, index)
				if filesystem.ismicropython():
					sys.stdout.write(line)
				else:
					sys.stdout.write(line.decode("utf8"))
		return differences

	def deinit_image(self, image):
		""" Release image allocated """
		if image:
			if not image in self.images:
				if image != self.image_background:
					image.deinit()

	def detect(self, display=True):
		""" Detect motion """
		detected = False
		change_polling = False

		# Compute the list of differences
		differences = self.compare(display)

		# Too many differences found
		if len(list(differences.keys())) >= self.config.threshold_motion:
			detected = True
			change_polling = True
		# If no differences
		elif len(list(differences.keys())) == 1:
			image = self.image_background
			self.image_background = self.images[0]
			self.deinit_image(image)
			detected = False
		# If not enough differences
		elif len(list(differences.keys())) <= self.config.threshold_glitch:
			detected = True
			change_polling = True
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
				if self.is_detected(image.get_comparison()):
					image.set_motion_detected()
		return detected, change_polling

class Detection:
	""" Asynchronous motion detection object """
	def __init__(self, pir_detection):
		""" Constructor """
		self.pir_detection = pir_detection
		self.load_config()
		self.motion = None

		if self.pir_detection is True:
			self.polling_frequency = 3
		else:
			self.polling_frequency = 100
		self.detection = None
		self.activated = None
		self.refresh_config_counter = 0
		self.last_detection = 0
		self.cadencer = NotificationCadencer()
		self.last_notification_suspended = 0

	def load_config(self):
		""" Load motion configuration """
		# Open motion configuration
		self.motion_config      = MotionConfig()
		self.motion_config.load_create()
		self.webhook_config      = WebhookConfig()
		self.webhook_config.load_create()

	def refresh_config(self):
		""" Refresh the configuration : it can be changed by web page """
		if self.refresh_config_counter % 11 == 0:
			# If configuration changed
			if self.motion_config.refresh():
				logger.syslog("Change motion config %s"%self.motion_config.to_string(), display=False)
				if self.motion:
					self.motion.refresh_config()
			# If configuration changed
			if self.webhook_config.refresh():
				logger.syslog("Change webhook config %s"%self.webhook_config.to_string(), display=False)
				if self.motion:
					self.motion.refresh_config()

		self.refresh_config_counter += 1

	async def run(self):
		""" Main asynchronous task """
		await tasking.Tasks.monitor(self.detect)

	async def detect(self):
		""" Detect motion """
		result = False
		# Wait the server resume
		await tasking.Tasks.wait_resume(name="motion")

		# Release previously alocated image
		self.release_image()

		# If the motion detection activated
		activated = await self.is_activated()
		if activated or self.is_permanent():
			try:
				# Capture motion
				result = await self.capture(activated)
			finally:
				# Release previously alocated image
				self.release_image()

		else:
			if self.motion:
				self.motion.stop_light()
			await uasyncio.sleep(10)
		self.cadencer.refresh()

		# Refresh configuration when it changed
		self.refresh_config()

		return result

	async def is_activated(self):
		""" Indicates if the motion detection is activated according to configuration or presence """
		result = False

		# If motion activated
		if self.motion_config.activated:
			# If motion must be suspended on presence
			if self.motion_config.suspend_on_presence:
				# If home is empty
				if Presence.is_detected() is False:
					result = True
			else:
				result = True

		# If state of motion changed
		if self.activated != result:
			# Force garbage collection
			collect()

			if result:
				Notifier.notify(topic=topic.motion_detection, value=topic.value_on, message=lang.motion_detection_on, enabled=self.motion_config.notify_state)
			else:
				Notifier.notify(topic=topic.motion_detection, value=topic.value_off, message=lang.motion_detection_off, enabled=self.motion_config.notify_state)
			self.activated = result

		# If camera activated and motion activated
		if Camera.is_activated() and result:
			result = True
		else:
			result = False

		# If motion disabled
		if result is False and self.is_permanent() is False:
			# Wait moment before next loop
			await uasyncio.sleep_ms(500)
		return result

	def is_permanent(self):
		""" Indicates if pemanent detection activated """
		result = False
		# If motion activated
		if self.motion_config.activated:
			# If detection permanent without notification activated
			if self.motion_config.permanent_detection:
				result = True
		return result

	async def init_motion(self):
		""" Initialize motion detection """
		firstInit = False

		# If motion not initialized
		if self.motion is None:
			self.motion = MotionCore(self.motion_config, self.pir_detection)
			if self.motion.open() is False:
				self.motion = None
				# pylint:disable=broad-exception-raised
				raise Exception("Cannot open camera")
			else:
				firstInit = True

		# If the camera configuration changed
		if video.Camera.is_modified() or firstInit:
			# Restore motion configuration
			self.motion.resume()
			video.Camera.clear_modified()

	def release_image(self):
		""" Release motion image allocated """
		# If detection
		if self.detection:
			message, image = self.detection
			# Release image buffer
			self.motion.deinit_image(image)

	async def capture(self, activated):
		""" Capture motion """
		result = False

		# If camera not stabilized speed start
		if self.motion and self.motion.is_stabilized() is True:
			frequency = self.polling_frequency*500 if tasking.Tasks.is_slow() else self.polling_frequency
			if frequency > 1000:
				while frequency > 0:
					await uasyncio.sleep_ms(500)
					frequency -= 500
					await tasking.Tasks.wait_resume(name="motion")
			else:
				await uasyncio.sleep_ms(frequency)

		try:
			# Waits for the camera's availability
			reserved = await video.Camera.reserve(self, timeout=1)

			# If reserved
			if reserved:
				# Initialize motion detection
				await self.init_motion()

				# Capture motion image
				self.detection = await self.motion.capture()

				# If motion detected and detection activated
				if self.detection is not None and activated is True:

					# Notify motion with push over
					message, image = self.detection

					# If no previous detection
					if self.last_detection == 0:
						# Send motion detected
						Notifier.notify(topic=topic.motion_detected, value=topic.value_on, url=self.webhook_config.motion_detected)

					self.last_detection = int(time.time())

					# If the notifications are not too frequent
					if self.cadencer.can_notify():
						Notifier.notify(topic=topic.motion_image, message=message, data=image.get(), enabled=self.motion_config.notify)
					else:
						logger.syslog("Notification '%s' too frequent ignored" %message)
				else:
					# If motion detected recently
					if self.last_detection > 0:
						# If no more motion detection
						if self.last_detection + STATE_DURATION < int(time.time()):
							# Send webhook no motion detected
							Notifier.notify(topic=topic.motion_detected, value=topic.value_off, url=self.webhook_config.no_motion_detected)
							self.last_detection = 0
				# Detect motion
				detected, change_polling = self.motion.detect()

				# If motion found
				if change_polling is True:
					# Speed up the polling frequency
					self.polling_frequency = 10
					Historic.set_motion_state(True)
				else:
					# Slow down the polling frequency
					self.polling_frequency = 50
					Historic.set_motion_state(False)
				result = True
			else:
				if self.last_notification_suspended + 120 < int(time.time()):
					self.last_notification_suspended = int(time.time())
					Notifier.notify(topic=topic.motion_detection, value=topic.value_suspended, message=lang.motion_detection_suspended, enabled=self.motion_config.notify_state)
				result = True

		finally:
			if reserved:
				await video.Camera.unreserve(self)
		return result

class MovingCounters:
	""" Manages an event counter with a history """
	def __init__(self, proof, step):
		""" Constructor, proof=indicates the depth of the history, step=duration in seconds of each history step """
		self.total = 0
		self.step = step
		self.counters = []
		for i in range(proof):
			self.counters.insert(0,[0,0])

	def refresh(self, increase=0):
		""" Refresh counter history, increase=1 forces the counter to increment else the counter history updated """
		t = int(time.time())

		if self.counters[-1][0] + self.step < t:
			self.total   -= self.counters[0][1]
			self.counters = self.counters[1:]
			self.counters.append([t,0])

		self.counters[-1][1] += increase
		self.total += increase

	def get_total(self):
		""" Returns the total value of the counted values. """
		return self.total

class NotificationCadencer(MovingCounters):
	""" Cadencer for motion detection notifications
	Parameters:
		batch (int):size of a notification batch before changing the wait time
		duration (int):duration in seconds to add when a batch has ended
		max_duration (int):max waiting value"""
	def __init__(self, batch=5, duration=15, max_duration=60):
		""" Constructor """
		MovingCounters.__init__(self, 20, 60)
		self.last = 0
		self.max_duration = max_duration
		self.duration = duration
		self.batch = batch

	def can_notify(self):
		""" Indicates whether a notification can be sent or not """
		self.refresh(0)

		total = self.get_total() // self.batch

		if total >= 1:
			duration = (1<<(total-1))*self.duration
			if duration > self.max_duration:
				duration = self.max_duration
		else:
			duration = 0

		t = int(time.time())
		if self.last + duration <= t:
			self.refresh(1)
			self.last = t
			result = True
		else:
			result = False
		return result
