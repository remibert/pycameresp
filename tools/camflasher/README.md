# camflasher
![](/tools/camflasher/icons/camflasher.ico "Camflasher")

Camflasher is a tool which allows to flash pycameresp firmware. It display all traces received from the device. It offer the possibility to access the esp32 shell, edit files from esp32 and execute them.

# Devices supported

Below are the devices compatible with pycameresp :

![ESP32CAM](/images/Device_ESP32CAM.jpg "ESP32CAM")
![ESP32CAM-MB](/images/Device_ESP32CAM-MB.jpg "ESP32CAM-MB")
![NODEMCU](/images/Device_NODEMCU.jpg "NODE MCU") ![LOLIN32](/images/Device_LOLIN32.jpg "LOLIN32")
![TTGO](/images/Device_TTGO.jpg "TTGO")
# Specific wiring for esp32cam

The ESP32-CAM does not have a usb connection, you have to add a usb/serial converter :

![Esp32camProgram.png](/images/Esp32camProgram.png "Esp32Cam flash firmware wiring")

Put jumper on GPIO 0 to GND for programming the firmware.
Remove it once the firmware has been programmed, press reset button after.

# Manual for flash firmware

- Download the firmware associated with your device :

	- [ESP32-CAM, ESP32-CAM-MB](https://github.com/remibert/pycameresp/releases/download/V3/ESP32CAM-firmware.bin)

	- [ESP32-NODEMCU, LOLIN32, ESP32 without SPIRAM ](https://github.com/remibert/pycameresp/releases/download/V3/GENERIC-firmware.bin)

	- [ESP32-TTGO-T8 or ESP32 with SPIRAM ](https://github.com/remibert/pycameresp/releases/download/V3/GENERIC_SPIRAM-firmware.bin)

- Download driver for your computer and install it :
	- [CH341 drivers](http://www.wch.cn/download/CH341SER_ZIP.html)

	- [CP210 drivers](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)

	- [FTDI drivers](https://ftdichip.com/drivers/vcp-drivers/)

- Download the camflasher application and unzip :
	- [Windows 10 64 bits](https://github.com/remibert/pycameresp/releases/download/V3/CamFlasher_win10_64.zip)

	- [Windows seven 64 bits](https://github.com/remibert/pycameresp/releases/download/V3/CamFlasher_win7_64.zip)

	- [OSX Big Sur Intel](https://github.com/remibert/pycameresp/releases/download/V3/CamFlasher_osx.zip)

	- [Debian x86_64](https://github.com/remibert/pycameresp/releases/download/V3/CamFlasher_linux.zip)

- Connect the device to the USB port of your computer.

- Start camFlasher

![CamFlasher](/images/0_CamFlasher.png "CamFlasher")

- Select flasher/flash to flash the firmware

![CamFlasher](/images/1_CamFlasher.png "CamFlasher")

- Select firmware and check "Erase flash" the first time

![CamFlasher](/images/2_CamFlasher_SelectFirmware.png "CamFlasher")

- The firmware write is displayed in the output window

![CamFlasher](/images/3_CamFlasher_Flashing.png "CamFlasher")

- At the end of writing the firmware a message is displayed. 

- Press reset button of device if necessary.

![CamFlasher](/images/4_CamFlasher_EndFlash.png "CamFlasher")

- The output window displays device traces

![CamFlasher](/images/5_CamFlasher_StartAccessPoint.png "CamFlasher")

- At the first time the wifi access point is started automaticaly.

- Connect your PC to the access point
	- Network name is **esp** followed by 5 digits. 
	- Password is **Pycam_** followed by the same 5 digits.


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

