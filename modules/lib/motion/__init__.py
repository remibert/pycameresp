# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class to manage motion detection with ESP32CAM """
from motion.motion import *
from motion.presence import *
from motion.historic import *
from tools import useful

def start(loop=None, onBattery=True, pirDetection=False):
	""" Start the asynchronous motion detection and presence detection """
	loop.create_task(detectPresence())
	if useful.iscamera():
		loop.create_task(detectMotion(onBattery, pirDetection))
		loop.create_task(Historic.periodicTask())
