# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class to manage motion detection with ESP32CAM """
from motion.motion import *
from motion.historic import *
from video.video import Camera
from tools import useful

def start(loop=None, pir_detection=False):
	""" Start the asynchronous motion detection and presence detection """
	if useful.iscamera() and Camera.is_activated():
		loop.create_task(detect_motion(pir_detection))
		loop.create_task(Historic.periodic_task())
