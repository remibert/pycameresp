# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Motion detection only work with ESP32CAM (Requires specially modified ESP32CAM firmware to handle motion detection.) """
import video.video
import tools.info
import tools.tasking

class Motion:
	""" Class to manage the motion capture """
	@staticmethod
	def start(**kwargs):
		""" Start motion detection """
		if tools.info.iscamera() and video.video.Camera.is_activated():
			from motion.motioncore import Detection
			detection = Detection(kwargs.get("pir_detection", False))
			tools.tasking.Tasks.create_monitor(detection.detect)
