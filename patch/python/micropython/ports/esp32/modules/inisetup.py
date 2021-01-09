import uos
from flashbdev import bdev


def check_bootsec():
    buf = bytearray(bdev.ioctl(5, 0))  # 5 is SEC_SIZE
    bdev.readblocks(0, buf)
    empty = True
    for b in buf:
        if b != 0xFF:
            empty = False
            break
    if empty:
        return True
    fs_corrupted()


def fs_corrupted():
    import time

    while 1:
        print(
            """\
FAT filesystem appears to be corrupted. If you had important data there, you
may want to make a flash snapshot to try to recover it. Otherwise, perform
factory reprogramming of MicroPython firmware (completely erase flash, followed
by firmware programming).
"""
        )
        time.sleep(3)


def setup():
    check_bootsec()
    print("Performing initial setup")
    uos.VfsLfs2.mkfs(bdev)
    vfs = uos.VfsLfs2(bdev)
    uos.mount(vfs, "/")
    with open("boot.py", "w") as f:
        f.write(
            """\
# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
"""
        )
    with open("yourpage.py","w") as f:
        f.write(
            """\
# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from server.httpserver import HttpServer
from htmltemplate import *
from webpage     import *

# Test simple page with button 
@HttpServer.addRoute(b'/yourpage', title=b"Your page", index=1000)
async def yourPage(request, response, args):
	page = mainPage(
		content=\
			[
				Container(
				[
					Br(),
					Tag(b"<p>Hello world</p>"),
					Br(),
					Command(text=b"Button",  path=b"ontest", id=b"onpressed" , class_=b"btn-info"),
				])
			], title=args["title"], active=args["index"], request=request, response=response)
	await response.sendPage(page)

# Called when the button pressed
@HttpServer.addRoute(b'/ontest/onpressed')
async def buttonPressed(request, response, args):
	print("button Pressed")
	await response.sendOk()
"""
        )
    with open("main.py", "w") as f:
        f.write(
            """\
# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
try:
	import uasyncio
except:
	import sys
	sys.path.append("lib")
	sys.path.append("simul")
import uasyncio
import machine
from tools.battery import Battery

machine.freq(240000000)

# Can only be done once at boot before start the camera and sd card
onBattery   = Battery.isActivated()

# If the power supply is the mains
if onBattery == False:
	# Create asyncio loop
	loop = uasyncio.get_event_loop()

	# Html pages loader
	def pageLoader():
		# The html pages only loaded when the connection of http server is done
		# This reduces memory consumption if the server is not used
		from webpage import mainpage

		try:
			# Insert your pages here
			from yourpage import yourPage
		except:
			# This page only available for example in the specific firmware
			pass

	import server

	# Start all server (Http, Ftp, Telnet) and start wifi manager
	# If you set the last parameter to True it preloads the pages of the http server at startup
	server.start(loop, pageLoader, False)
else:
	# Check if PIR detection
	isPinWakeUp = Battery.isPinWakeUp()
	print("Detection %s"%(isPinWakeUp))

	# Check the battery level and force deepsleep is to low
	Battery.protect()

	# Create asyncio loop
	loop = uasyncio.get_event_loop()

from tools import useful

# If camera is available (required specific firmware)
if useful.iscamera():
	# Start motion detection (only used with ESP32CAM)
	import motion 
	motion.start(loop, onBattery, isPinWakeUp)

# Run asyncio for ever
loop.run_forever()
"""
        )
    return vfs
