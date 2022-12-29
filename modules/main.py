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

# Create battery charge monitoring (Must be always be first)
pycameresp.create_battery_task(loop)

# Define the type of camera device
device = "ESP32CAM" # "ESP32ONE" "M5CAMERA-B"

# Create camera and motion detection asynchronous task
pycameresp.create_camera_task(loop, device)

# from server import openmeteo

# Sample of user task
# async def meteo_task():
# 	""" Get meteo from openmeteo """
# 	while True:
# 		await openmeteo.async_get_meteo(b"?latitude=52.52&longitude=13.41&hourly=temperature_2m,relativehumidity_2m,windspeed_10m")
# 		await uasyncio.sleep(1)

# Register the user task, monitor all exceptions
# pycameresp.create_user_task(loop, meteo_task)

def sample_html_page_loader():
	""" Html page loader. Html pages are loaded in memory only when the web server is used """
	try   :
		import sample
	except:
		pass
	try:
		import electricmeter
	except:
		pass

try:
	from electricmeter import create_electric_meter
	create_electric_meter(loop, gpio=21)
except Exception as err:
	print(err)

# Create servers, network tools, wifi manager asynchronous task
pycameresp.create_network_task(loop, sample_html_page_loader)

# Create shell asynchronous task
pycameresp.create_shell_task(loop)

# Start all asynchronous tasks
pycameresp.run_tasks(loop)
