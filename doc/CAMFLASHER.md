[Main page](/README.md)

# Installation manual
![](/tools/camflasher/icons/camflasher.ico "Camflasher")

Camflasher is a tool which allows to flash pycameresp firmware. It display all traces received from the device. 

It offer the possibility to access the esp32 shell, edit files from esp32 and execute them.

It is also a VT100 console which allows to operate the text editor, and to display colored texts thanks to the VT100 escape sequences. Not all VT100 commands are supported, but the most common ones are available.

Camflasher with shell commands **upload** and **download**, allows to upload or download files easily from the device.

- Download computer drivers for your device :
	- [CH341 drivers](http://www.wch.cn/download/CH341SER_ZIP.html)
	- [CP210 drivers](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)
	- [FTDI drivers](https://ftdichip.com/drivers/vcp-drivers/)

- Download the firmware associated with your device :

	- [ESP32-CAM, ESP32-CAM-MB, ESP32ONE, M5Stack Camera](https://github.com/remibert/pycameresp/releases/download/V15/ESP32CAM-firmware.bin)

	- [ESP32-TTGO-T8 or ESP32 with SPIRAM ](https://github.com/remibert/pycameresp/releases/download/V15/GENERIC_SPIRAM-firmware.bin)


- Or download the zip for standard micropython firmware :

	- [Shell with editor](https://github.com/remibert/pycameresp/releases/download/V15/shell.zip)

	- [Wifi manager, Http server](https://github.com/remibert/pycameresp/releases/download/V15/server.zip)

- Text editor source files running on python3 and micropython :

	- [Text editor](https://github.com/remibert/pycameresp/releases/download/V15/editor.zip)

It is possible to run the shell with editor, or the servers on a standard micropython platform. The servers, the wifi manager, requires having enough ram and wifi support (ESP32 with SPIRAM for example). Unzip archive and install it with rshell.



- Download the camflasher application and unzip it :
	- [CamFlasher for Windows 10 64 bits](https://github.com/remibert/pycameresp/releases/download/V15/CamFlasher_windows_10_64.zip)

	- [CamFlasher for OSX Ventura Intel](https://github.com/remibert/pycameresp/releases/download/V15/CamFlasher_osx_i386.zip)

	- [CamFlasher for OSX Ventura M1](https://github.com/remibert/pycameresp/releases/download/V15/CamFlasher_osx_arm.zip)

	- [CamFlasher for Debian 11 x86_64](https://github.com/remibert/pycameresp/releases/download/V15/CamFlasher_linux.zip)

		- On linux to be able to operate without being a super user you must enter the commands :

			- sudo usermod -a -G dialout $USER
			- sudo chmod 666 /dev/ttyUSB0<br>

- Connect the device to the USB port of your computer.

- Start camFlasher

![CamFlasher](/images/0_CamFlasher.png "CamFlasher")

- Select Flasher/Esptool.py to flash the firmware

- [See specific wiring for esp32cam with serial connector](/doc/WIRING_ESP32CAM.md)

![CamFlasher](/images/1_CamFlasher.png "CamFlasher")

- Select firmware and check "Erase flash" the first time. The firmware can be download directly from web site. 
- For Esp32 S3 the address must be 0x0
- For others Esp32 the address must be 0x1000.

**If the device resets in a loop, it is necessary to do a flash with erase**.

![CamFlasher](/images/2_CamFlasher_SelectFirmware.png "CamFlasher")

- The firmware write is displayed in the console.

![CamFlasher](/images/3_CamFlasher_Flashing.png "CamFlasher")

- At the end of writing the firmware a message is displayed. 

- Press reset button of device if necessary.

![CamFlasher](/images/4_CamFlasher_EndFlash.png "CamFlasher")

- The console window displays device traces

![CamFlasher](/images/5_CamFlasher_StartAccessPoint.png "CamFlasher")

- At the first time the wifi access point is started automaticaly.

![CamFlasher](/images/6_CamFlasher_DetailAccessPoint.png "CamFlasher")

- Connect your computer to the access point
	- Wifi network name (SSID) is **esp??????** access point (????? = decimal value). 
	- Wifi Password is **Pycam_?????** (????? = same value as the hexa part of the ssid).

# Connection on the device

- Open a web browser with the address http://192.168.3.1

Below is the menu of the web application to configure the device :
![WebMenu](/images/WebMenu_All.png "WebMenu")

Note : **The presentation of the menu can be much less beautiful than this as long as the style sheet css has not yet been loaded.**

# Menu details

The **Account** submenu allows you to configure the password, the language :

![WebMenu](/images/WebMenu_Account.png "WebMenu")

The **System** submenu allows you to request a reboot, obtain information on the device, configure the wake up and the battery mode :

![WebMenu](/images/WebMenu_System.png "WebMenu")

The **Network** submenu is used to configure the access point and wifi networks :

![WebMenu](/images/WebMenu_Network.png "WebMenu")

The **Server** submenu allows the activation/deactivation of each server, to configure pushover notifications, and to configure the presence detection of smartphones to automate the start/stop of motion detection :

![WebMenu](/images/WebMenu_Server.png "WebMenu")

The **Camera** submenu allows to see the streaming of the camera, and also to activate/deactivate the camera :

![WebMenu](/images/WebMenu_Camera.png "WebMenu")

The **Motion** submenu allows you to start and stop motion detection, configure motion detection, and view detection history :

![WebMenu](/images/WebMenu_Motion.png "WebMenu")

# Region settings

You can configure the time zone offset to synchronize the time as well as the language (french and english). The language will only be taken into account at the next reboot.

- Select the **Account**/**Region**

![WebMenu](/images/WebMenu_Region.png "WebMenu")

- click on **Modify** button
- change the values
- click on **Save** button to apply changes

# User password settings

You can currently only define one user, it will be useful for all servers (http, ftp, telnet).

- Select the **Account**/**User/Password**

![WebMenu](/images/WebMenu_Password.png "WebMenu")

- Enter name and password twice
- Click on **Modify password**


# Wifi network configuration

At the first use you must configure the wifi :

- Select the **Network**/**Wifi**

![WebMenu](/images/WebMenu_Wifi.png "WebMenu")

Click on **Modify** to configure a wifi access.

To enable wifi check **Activated** (checked by default).

The **Hostname** allows you to connect to the device with a server name rather than an ip address. The suffix of the name depends on your internet box, on my box it is ".home", in the example above this will give the url to enter in your browser ```http://esp33665.home```.

Enter the ssid of your network, as well as the password then click on **Save** button to apply changes.

If you have several possible networks, just re-enter an ssid/password and click on **Save** button.

The **&lt;-** and **-&gt;** buttons to navigate in the different networks registered.

The **Forget** button delete a saved wifi network.

The **Set Default** button force the priority connection on this network.

The check **Automatic start of access point when the wifi is not reachable** is used for a fallback, by default the access point is inactive, but if it is impossible to connect on wifi network, it can be activated (depend of the check value). This is very useful if you take your device with you on a trip, and want to connect to it, without having to use a wifi network. Note that the activation of the access point produce disturbances on the video images, which can in case of weak light produce motion detections.

It is also possible to enter a fixed ip address, uncheck **Dynamic IP** :

![WebMenu](/images/WebMenu_IpFixed.png "WebMenu")

# Access point configuration

You can configure the access point.
- select the **Network**/**Access point**
- click on **Modify** button
- change values
- click on **Save** button to apply changes

![WebMenu](/images/WebMenu_AccessPoint.png "WebMenu")

# Server activation

You can enable/disable servers or services, for this you must : 
- select the menu **Server**/**Configuration**
- click on **Modify** button,
- check or uncheck your choices,
- click on **Save** button to apply changes

Be careful when you deactivate **Http**, it automatically deactivates the web interface on the next restart.

![WebMenu](/images/WebMenu_ServerActivation.png "WebMenu")

# Smartphone notification

It is possible to send notifications on smartphones, this uses an application available on iOS, Android and Window. You need to install the app [Push over](https://pushover.net).

On the pushover smartphone application :
- create an account,
- create a device (your smartphone or tablet),

You get then get **User key**

- go to web browser and open https://pushover.net, 
- search in the settings page **Your Applications**, 
- click on link **Create an Application/API Token** :
  - enter name (notification source name), 
  - add description and icon (if you want), 
  - check the contract of service, 
  - and click on **Create Application**. 

You then get **API Token/Key**

Return your device configuration page :
- select **Server**/**Notification**

![WebMenu](/images/WebMenu_PushOver.png "WebMenu")

- click on **Modify** button
- check **Activated**
- fill the **User key** field with the value obtained previously
- fill the **API token** field with the value obtained previously
- click on **Save** button to apply changes

You should then receive a notification on your smartphone.

# Presence detection 

The motion detector can be automatically started in your absence, and automatically stopped in your presence.

For this, pycameresp detects the presence of your smartphone on the wifi network.

To do this work permanently, it is necessary to configure your internet box, so gives a network name to your smartphone.

![Example of orange box](/images/WebMenu_NamingSmartphone.png)

Return on your device configuration page :
- select **Server**/**Presence**

![WebMenu](/images/WebMenu_Presence.png "WebMenu")

- click on **Modify** button
- check **Activated**
- enter ip address of your smartphone
- check **Convert ip address to DNS name** to translate ip address
- check or uncheck **Notification** if you want to be notified each time the smartphone appears and disappears on the network
- click on **Save** button to apply changes

# Camera setting

You can see the camera in streaming, and thus adjust its orientation.

- select **Camera**/**Video stream**

![WebMenu](/images/WebMenu_Streaming.png "WebMenu")

# Motion detection setting

You can configure the motion detection.

- select **Motion**/**Configuration**

![WebMenu](/images/WebMenu_MotionSetting.png "WebMenu")

- click on **Modify** button
- check **Activated**
- color in blue on the video image the parts that will be insensitive to motion detection (click to toggle), **Clear** button erase all, **Set** button set all.
- check the switches you want to activate
- click on **Save** button to apply changes

Sensitivity adjustment requires long-term experimentation. At first leave the default settings, but if you get too many notifications, you will have to hide the areas you don't want to monitor, increase the detection size, or decrease the sensitivity.

The placement of the camera is essential to avoid too many notifications, it must be pointed at an area that moves little, preferably indoors, and if it is placed outdoors, it is necessary to hide any area of vegetation that can move by large wind, or sky or busy roads. You must also fix it on a rigid support which does not vibrate, any small displacement can cause motion detection.

# Motion historic

If you have pushover notifications enabled, you will receive all detections on this app, but you can also view all detections and see which areas triggered the notification.

- select **Motion**/**Historic**

![WebMenu](/images/WebMenu_MotionHistoric.png "WebMenu")

The red frames indicate the areas that have triggered a notification.

Action on the image :

- ⏮ : click on top left corner of image switches to first motion detection (also page up key)
- ⏭ : bottom right corner of image switches to last motion detection (also page down key)
- ⏪ : click on the top of the image to switches to the previous day of motion detection (also up arrow key)
- ⏩ : click on the bottom of the image switches to the next day of motion detection (also down arrow key)
- ◀️ : click on the left of the image switches to the previous motion detection (also left arrow key)
- ▶️ : click on the left of the image switches to the next motion detection (also right arrow key)
- ⏺ : click in the middle of the image to save the image on your computer

The image information is : 
- **YYYY/MM/DD hh:mm:ss** : date and time of the motion detection,
- **Id=xxx** : identification number of the images since the launch of the detection,
- **D=xxx** : number of squares in the image that have changed since the previous image (see red frames).

# System menu

The system menu a lot of different things. It allows reboot, file exchange, get syslog, battery configuration and scheduled wake up. Attention concerning the battery, this mode puts the device on standby and only wakes it up on an event on one of these pins, so it can no longer respond to telnet, web interface or ftp.

# Specific camera configuration
- For **M5Stack** with camera, edit the main.py and change the ```device="ESP32CAM"``` by
```device="M5CAMERA-B"```.
- For **Esp32ONE**, edit the main.py and change the ```device="ESP32CAM"``` by ```device="ESP32ONE"```.

Note: the **Esp32ONE** does not allow the camera to operate at the same time as the sd card.

# Shell access

On the CamFlasher application, when the device has finished booting, press any key on the keyboard.

This suspends the current servers, and gives access to the shell from the device.

![Shell access](/images/11_CamFlasherShell.png)


![Edit file](/images/12_CamFlasherEdit.png)

[See shell commands](/doc/SHELL.md)

# Text editor

From the shell you can edit the files with text editor on the device, with **edit** command line. 

![Execute file](/images/13_CamFlasherExecute_1.png)

This editor work also in telnet, then you can edit file on remote device.

![Execute file](/images/13_CamFlasherExecute_2.png)

You can also execute directly from the text editor, the script being edited with the **F5** key :

![Execute file](/images/13_CamFlasherExecute_3.png)

All this is done directly from the device.

[Keyboard shortcuts of text editor](/doc/EDITOR.md)

Enter the **exit** command to restart the servers.

Enter the **quit** command to access the python prompt.

# Upload or download files

You can exchange files between pc and device. The working directory, allows you to locate the directory on your computer to exchange files. See in options :

![Working directory](/images/15_CamFlasher_WorkingDir.png "Working directory definition")


The shell command **download** allows the downloading files from board to your computer.

The shell command **upload** allows the uploading files from your computer into the device.

The "-r" option offers recursion. Wildcard are supported for these commands.

Drop a file, a directory or the contents of a zip is possible (it also works in telnet connection) :

![Drop.gif](/images/Drop.gif "Drop file on CamFlasher")

# Working with standard micropython

Except the camera part, all the sources work on a standard micropython. However, there are limitations. On an esp32 without spiram, the source code cannot work because the RAM is not sufficient. In this case it is imperative to load firmware modified, when the code is in ROM, it consumes much less RAM. With an esp32 with spiram, you can install the precompiled python scripts (micropython **1.19.1** compatible).

You must go to the shell prompt or the python prompt.

![Upload shell server](/images/16_CamFlasher_UploadShell.png "Upload shell or server")

If you select **Upload shell**, it will only download the shell and the text editor. This case works perfectly on a Pico PI RP02 as well as all esp32.

If you select **Upload server**, you will also have the web server, ftp, wifimanager. **This download overwrites the main.py, so if you have modified it, you will have to save it first.**

This automatically downloads the latest version from github.

![Upload shell server](/images/17_CamFlasher_UploadShell.png "Upload shell or server")
![Upload shell server](/images/18_CamFlasher_UploadShell.png "Upload shell or server")

To start the shell, enter the commands :
```
>>> from shell import sh
>>> sh()
```


# Console configuration

You can change the console display colors, as well as the character font. See Console/Option menu.

![Option](/images/14_CamFlasher_Option.png)

# VT100 colors supported

Below is the list of supported VT100 colors codes :

![Option](/images/19_CamFlasher_VTColorsSupported.png)