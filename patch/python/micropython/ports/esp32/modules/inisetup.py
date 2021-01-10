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
    with open("welcome.py","w") as f:
        f.write(
            """\
# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from server.httpserver import HttpServer
from htmltemplate import *
from webpage     import *

# Test simple page with button 
@HttpServer.addRoute(b'/welcome', title=b"Welcome", index=0)
async def welcomePage(request, response, args):
	page = mainPage(
		content=\
			[
				Container(
				[
					Br(),
					Tag(b'''
<p>
	To get notifications on your smartphone, you need to install the app <a href="https://pushover.net">Push over</a>, create an account, 
	and create an Application/API Token.

	To use motion detection on ESP32CAM you have to configure :
	<ul>
		<li><a href="wifi">Set wifi SSID and password and activate it</a></li>
		<li><a href="accesspoint">Disable the access point for more security</a></li>
		<li><a href="server">Choose available server</a></li>
		<li><a href="changepassword">Enter password and user for more security</a></li>
		<li><a href="pushover">Create push over token and user to receive motion detection image</a></li>
		<li><a href="motion">Activate and configure motion detection</a></li>
		<li><a href="camera">See the rendering of the camera to adjust its position</a></li>
		<li><a href="battery">Configure the battery mode<a></li>
		<li><a href="/">See all information about the board</a></li>
	</ul>
	Don't forget to activate what you want to work.
</p>
<p>
	<b>Be careful, the battery mode activations produces deep sleeps, and all the servers are no longer accessible. Only activate it if you know what you are doing.</b>
</p>
<p>This page can be easily removed by deleting the <b>welcome.py</b> file</p>
<p>Below is an example of a button that reacts with the python script</p>
'''),
					Br(),
					Command(text=b"Click me",  path=b"onbutton", id=b"clicked" , class_=b"btn-info"),
				])
			], title=args["title"], active=args["index"], request=request, response=response)
	await response.sendPage(page)

# Called when the button pressed
@HttpServer.addRoute(b'/onbutton/clicked')
async def buttonPressed(request, response, args):
	print("Button clicked")
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
	from tools import useful
	isPinWakeUp = False

	# Create asyncio loop
	loop = uasyncio.get_event_loop()

	# Html pages loader
	def pageLoader():
		# The html pages only loaded when the connection of http server is done
		# This reduces memory consumption if the server is not used
		from webpage import mainpage
		from server.httpserver import HttpServer

		try:
			# Welcome page (can be suppressed)
			from welcome import welcomePage
		except ImportError as err:
			pass

	import server

	# Start all server (Http, Ftp, Telnet) and start wifi manager
	# If you set the last parameter to True it preloads the pages of the http server at startup
	server.start(loop, pageLoader, False)
	isPinWakeUp = False
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
