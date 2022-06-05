# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET

# pylint:disable=wrong-import-order
# pylint:disable=wrong-import-position
# pylint:disable=unused-import
# pylint:disable=redefined-outer-name

""" Main module """
import pycameresp
import uasyncio

# Create asynchronous loop for all tasks
loop = uasyncio.get_event_loop()

# Checks if the battery is not too discharged
pycameresp.protect_battery()

# Define the type of camera device
device = "ESP32CAM" # "ESP32ONE" "M5CAMERA-B"

# Add camera and motion detection asynchronous task
pycameresp.add_camera_task(loop, device)

def sample_html_page_loader():
	""" Html page loader. Html pages are loaded in memory only when the web server is used """
	import sample

# Add servers and network tools asynchronous task
pycameresp.add_servers_task(loop, sample_html_page_loader)

# Add shell asynchronous task
pycameresp.add_shell_task(loop)

# Start all asynchronous tasks
pycameresp.run_tasks(loop)
