[Main page](/README.md)

# Firmware installation with CamFlasher application
![](/tools/camflasher/icons/camflasher.ico "Camflasher")

Camflasher is a tool which allows to flash pycameresp firmware. It display all traces received from the device. 

It offer the possibility to access the esp32 shell, edit files from esp32 and execute them.

It is also a VT100 console which allows to operate the text editor, and to display colored texts thanks to the VT100 escape sequences. Not all VT100 commands are supported, but the most common ones are available.

Camflasher with shell commands **importer** and **exporter**, allows to inject or retrieve files easily and quickly from the device.



- Download computer drivers for your device :
	- [CH341 drivers](http://www.wch.cn/download/CH341SER_ZIP.html)
	- [CP210 drivers](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)
	- [FTDI drivers](https://ftdichip.com/drivers/vcp-drivers/)


- Download the firmware associated with your device :

	- [ESP32-CAM, ESP32-CAM-MB](https://github.com/remibert/pycameresp/releases/download/V3/ESP32CAM-firmware.bin)

	- [ESP32-NODEMCU, LOLIN32, ESP32 without SPIRAM ](https://github.com/remibert/pycameresp/releases/download/V3/GENERIC-firmware.bin)

	- [ESP32-TTGO-T8 or ESP32 with SPIRAM ](https://github.com/remibert/pycameresp/releases/download/V3/GENERIC_SPIRAM-firmware.bin)

- Download the camflasher application and unzip it :
	- [CamFlasher for Windows 10 64 bits](https://github.com/remibert/pycameresp/releases/download/V3/CamFlasher_win10_64.zip)

	- [CamFlasher for Windows seven 64 bits](https://github.com/remibert/pycameresp/releases/download/V3/CamFlasher_win7_64.zip)

	- [CamFlasher for OSX Big Sur Intel](https://github.com/remibert/pycameresp/releases/download/V3/CamFlasher_osx.zip)

	- [CamFlasher for Debian x86_64](https://github.com/remibert/pycameresp/releases/download/V3/CamFlasher_linux.zip)

- Connect the device to the USB port of your computer.

- Start camFlasher

![CamFlasher](/images/0_CamFlasher.png "CamFlasher")

- Select flasher/flash to flash the firmware

- [See specific wiring for esp32cam with serial connector](/doc/WIRING_ESP32CAM.md)

![CamFlasher](/images/1_CamFlasher.png "CamFlasher")

- Select firmware and check "Erase flash" the first time.

**If the device resets in a loop, it is necessary to do a flash with erase**.

![CamFlasher](/images/2_CamFlasher_SelectFirmware.png "CamFlasher")

- The firmware write is displayed in the console window

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

# Device wifi initialization

- Open a web browser with the address http://192.168.3.1

- Select the Network/wifi

![CamFlasher](/images/1_PycamInitWifi.png "CamFlasher")

- Click on "Modify" button

![CamFlasher](/images/2_PycamInitWifi.png "CamFlasher")

- Enter your wifi network and your password.
- You can change the network name of the device. It will be easier to connect to it by doing http://devicename.home from your browser. The ".home" depends on your internet box and is automatically added by it.
- Click on "Save" button
- At next device restart it will automatically connect to your wifi network.

**In case of no connection to your wifi, the access point is automatically activated after a after a number of unsuccessful attempts. For your security, it is important to change the default password of the access point, or disable automatic start.**

# Other setup web pages

- (http://192.168.3.1/wifi) Set wifi SSID and password and activate it
- (http://192.168.3.1/accesspoint) Disable the access point for more security
- (http://192.168.3.1/server) Choose available server
- (http://192.168.3.1/changepassword) Enter password and user for more security
- (http://192.168.3.1/pushover) Create push over token and user to receive motion detection image
- (http://192.168.3.1/motion) Activate and configure motion detection
- (http://192.168.3.1/presence) Configuring your presence detection
- (http://192.168.3.1/camera) See the camera streaming to adjust its position
- (http://192.168.3.1/battery) Configure the battery mode

To get notifications on your smartphone, you need to install the app [Push over](https://pushover.net), create an account, 
and create an Application/API Token.

Don't forget to activate what you want to work.

**Be careful, the battery mode activations produces deep sleeps, and all the servers are no longer accessible. Only activate it if you know what you are doing.**


# Presence detection 

The motion detector can be automatically started in your absence, and automatically stopped in your presence.

For this, pycameresp detects the presence of your smartphone on the wifi network.

To do this work permanently, it is necessary to configure your internet box, so gives a network name to your smartphone.

![Example of orange box](/images/10_CamFlasher_NamingSmartphone.png)

# Shell access

On the CamFlasher application, when the device has finished booting, press any key on the keyboard.

This suspends the current servers, and gives access to the shell from the device.

![Shell access](/images/11_CamFlasherShell.png)

[See shell commands](/doc/SHELL.md)

# Text editor

From the shell you can edit the files with text editor on the device, with **edit** command line. This editor work in telnet, then you can edit file on remote device.

![Edit file](/images/12_CamFlasherEdit.png)

You can also execute directly from the text editor, the script being edited with the **F5** key :

![Execute file](/images/13_CamFlasherExecute.png)

All this is done directly from the device.

[See text editor](/doc/EDITOR.md)