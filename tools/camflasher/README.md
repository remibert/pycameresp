# camflasher
![](/tools/camflasher/icons/camflasher.ico "Camflasher")

Camflasher is a tool which allows to flash pycameresp firmware. It display all traces received from the device. It offer the possibility to access the esp32 shell, edit files from esp32 and execute them.

# Firmwares and devices supported

Below are the devices compatible with pycameresp :

![ESP32CAM](/images/Device_ESP32CAM.jpg "ESP32CAM") ![ESP32CAM-MB](/images/Device_ESP32CAM-MB.jpg "ESP32CAM-MB")

[ESP32-CAM, ESP32-CAM-MB](https://github.com/remibert/pycameresp/releases/download/V2/ESP32CAM-firmware.bin)

![NODEMCU](/images/Device_NODEMCU.jpg "NODE MCU") ![LOLIN32](/images/Device_LOLIN32.jpg "LOLIN32")

[ESP32-NODEMCU, LOLIN32, ESP32 without SPIRAM ](https://github.com/remibert/pycameresp/releases/download/V2/GENERIC-firmware.bin)

![TTGO](/images/Device_TTGO.jpg "TTGO")

[ESP32-TTGO-T8 or ESP32 with SPIRAM ](https://github.com/remibert/pycameresp/releases/download/V2/GENERIC_SPIRAM-firmware.bin)

# Drivers for your computer

A driver can be required by your computer, all drivers are below, select the driver required by your device and your computer :

- [CH341 drivers](http://www.wch.cn/download/CH341SER_ZIP.html)

- [CP210 drivers](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)

- [FTDI drivers](https://ftdichip.com/drivers/vcp-drivers/)

# Specific wiring for esp32cam

The ESP32-CAM does not have a usb connection, you have to add a usb/serial converter :

![Esp32camProgram.png](/images/Esp32camProgram.png "Esp32Cam flash firmware wiring")

Put jumper on GPIO 0 to GND for programming the firmware.
Remove it once the firmware has been programmed, press reset button after.



