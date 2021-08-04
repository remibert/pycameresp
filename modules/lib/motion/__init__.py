# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class to manage motion detection with ESP32CAM """
from motion.motion import *
from motion.historic import *
from tools import useful

def start(loop=None, pirDetection=False):
	""" Start the asynchronous motion detection and presence detection """
	if useful.iscamera():
		loop.create_task(detectMotion(pirDetection))
		loop.create_task(Historic.periodicTask())
