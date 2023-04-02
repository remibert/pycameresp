# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Main module """
import pycameresp

# Define the type of camera device
device = "ESP32CAM" # "ESP32ONE" "M5CAMERA-B"

pycameresp.start(device=device, battery=True, mqtt=True, ftp=True, wanip=True, webhook=True, ntp=True, http=True, telnet=True, pushover=True, presence=True, motion=True, starter=True, shell=True)
