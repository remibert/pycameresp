# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from server.httpserver import HttpServer
from htmltemplate import Br,ButtonCmd,Option,SwitchCmd,Tag,SliderCmd,ComboCmd,Paragraph
from webpage     import mainFrame
from tools       import useful

# Called when the button pressed
@HttpServer.addRoute(b'/sample/button')
async def buttonPressed(request, response, args):
	print("Button clicked")
	await response.sendOk()

# Called when the slider state changed
@HttpServer.addRoute(b'/sample/slider')
async def sliderChanged(request, response, args):
	print("Slider change to %d"%int(request.params[b"value"]))
	await response.sendOk()

# Called when the combo state changed
@HttpServer.addRoute(b'/sample/combo')
async def comboChanged(request, response, args):
	print("Number %s selected"%useful.tostrings(request.params[b"value"]))
	await response.sendOk()

# Called when the switch state changed
@HttpServer.addRoute(b'/sample/switch')
async def switchChanged(request, response, args):
	print("Switch change to %s"%useful.tostrings(request.params[b"value"]))
	await response.sendOk()

# Test simple page with button 
@HttpServer.addRoute(b'/welcome', title=b"Welcome", index=0)
async def welcomePage(request, response, args):
	page = mainFrame(request, response, args, b"Welcome",
		Tag(b'''
			<p>
				To get notifications on your smartphone, you need to install the app <a href="https://pushover.net">Push over</a>, create an account, 
				and create an Application/API Token.
				<br>
				<br>
				Configuration steps : 
				<ul>
					<li><a href="wifi">Configure the wifi connection</a></li>
					<li><a href="accesspoint">Configure the wifi access point</a></li>
					<li><a href="server">Select the available servers and the time setting</a></li>
					<li><a href="changepassword">Choose a username and password for security</a></li>
					<li><a href="pushover">Configure notifications on smartphones</a></li>
					<li><a href="motion">Configure motion detection and choose areas to ignore</a></li>
					<li><a href="camera">See the video rendering of the camera to adjust its position</a></li>
					<li><a href="battery">Configure wake-up and battery level management<a></li>
					<li><a href="system">Backup configuration and execution traces<a></li>
					<li><a href="/">Show informations about the board</a></li>
				</ul>
			</p>
			<br>
			<p>Example to interact with esp32 via an html page (see <b>welcome.py</b>)</p>
			'''),
			ButtonCmd(text=b"Click on button",  path=b"/sample/button"), Br(),Br(),
			SliderCmd(min=b"10", max=b"30", step=b"2", value=b"12", text=b"Move slider", path=b"/sample/slider"), Br(),
			ComboCmd(\
				[
					Option(value=b"One"   , text=b"One"),
					Option(value=b"Two"   , text=b"Two", selected=True),
					Option(value=b"Three" , text=b"Three"),
				], path=b"/sample/combo", text=b"Select number"), Br(),Br(),
			SwitchCmd(text=b"Change this switch", checked=True, path=b"/sample/switch"),
			Br(),
			Br(),
			Paragraph(b"You can eliminate this page by deleting the file <b>welcome.py</b> file"))
	await response.sendPage(page)

