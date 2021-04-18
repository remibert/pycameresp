# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from server.httpserver import HttpServer
from htmltemplate import *
from webpage     import *

# Test simple page with button 
@HttpServer.addRoute(b'/welcome', title=b"Welcome", index=0)
async def welcomePage(request, response, args):
	page = mainFrame(request, response, args, b"Welcome",
		Tag(b'''
			<p>
				To get notifications on your smartphone, you need to install the app <a href="https://pushover.net">Push over</a>, create an account, 
				and create an Application/API Token.

				To use motion detection on ESP32CAM you have to configure :
				<ul>
					<li><a href="wifi">Set wifi SSID and password and activate it</a></li>
					<li><a href="accesspoint">Change or disable the access point for more security</a></li>
					<li><a href="server">Choose available servers</a></li>
					<li><a href="changepassword">Enter password and user for more security</a></li>
					<li><a href="pushover">Create pushover token and user to receive motion detection image</a></li>
					<li><a href="motion">Activate and configure motion detection</a></li>
					<li><a href="camera">See the rendering of the camera to adjust its position</a></li>
					<li><a href="battery">Configure the battery mode<a></li>
					<li><a href="/">See all information about the board</a></li>
				</ul>
			</p>
			<p>
				<b>Be careful, the battery mode activations produces deep sleeps, and all the servers are no longer accessible. Only activate it if you know what you are doing.</b>
			</p>
			<p>This page can be easily removed by deleting the <b>welcome.py</b> file</p>
			'''))
	await response.sendPage(page)

