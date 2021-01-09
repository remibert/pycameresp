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
<p>Features :
	<ul>
		<li>Http web server </li>
		<li>Ftp server </li>
		<li>Telnet server</li>
		<li>User, password manager (for all servers)</li>
		<li>Web configuration</li>
		<li>Ntp synchronization</li>
		<li>Wifi manager</li>
		<li>Html template engine using <a href="https://jquery.com">jquery</a>, <a href="https://www.w3schools.com/bootstrap4">bootstrap 4</a></li>
		<li><a href="https://pushover.net">Push over</a> notification with image</li>
		<li>Shell usable on board</li>
		<li>True VT100 text editor usable on board, allows to execute python scripts during edition</li>
		<li>Battery management with detection level</li>
	</ul>
</p>

<p>
	On ESP32CAM to use motion detection with image notification, you have to configure :
	<ul>
		<li><a href="wifi">Activate wifi and configure it</a></li>
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

