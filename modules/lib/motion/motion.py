# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Motion detection only work with ESP32CAM (Requires specially modified ESP32CAM firmware to handle motion detection.) """
from video.video     import Camera
from tools import info,tasking

class Motion:
	""" Class to manage the motion capture """
	@staticmethod
	def start(**kwargs):
		""" Start motion detection """
		if info.iscamera() and Camera.is_activated():
			from motion.motioncore import Detection
			detection = Detection(kwargs.get("pir_detection", False))
			tasking.Tasks.create_monitor(detection.detect)
