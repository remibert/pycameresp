# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=wrong-import-order
""" Main module """
import pycameresp
import uasyncio

# Create asynchronous loop for all tasks
loop = uasyncio.get_event_loop()

# Create battery charge monitoring (Must be always be first)
pycameresp.create_battery_task(loop)

# Define the type of camera device
device = "ESP32CAM" # "ESP32ONE" "M5CAMERA-B"

# Create camera and motion detection asynchronous task
pycameresp.create_camera_task(loop, device)

# Create presence detection task (determine if an occupant is present in the house)
pycameresp.create_presence_task(loop)

# Create servers, network tools, wifi manager asynchronous task
pycameresp.create_network_task(loop)

# Create shell asynchronous task
pycameresp.create_shell_task(loop)

# Start all asynchronous tasks
pycameresp.run_tasks(loop)
