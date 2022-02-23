Pycameresp is designed to be a completely autonomous motion detector on ESP32-CAM. It can also works on other Esp32 with SPIRAM and on NodeMCU Esp32 but with some limitations, it is necessary to select the correct firmware for your device.

The firmware is based on an improved version of [micropython](http://micropython.org), it is ready to use because all pycameresp modules are embedded in the firmware (for boost performance and saving RAM).
But it is a standard micropython platform, the start of pycameresp is in the main.py, and therefore fully modifiable.

----

The firmware features are :
- Real-time motion detection with camera (ESP32-CAM)
- Smartphones notifications
- Live video stream of camera (ESP32-CAM)
- Configuration and consultation web page
- Smartphone presence detection on the wifi network (automatic activation/deactivation of motion detection)
- Shell to enter command lines with text editor executed directly on the device
- WiFi manager with automatic recovery after loss of radio signal
- Synchronization of the internal clock with ntp server, to be always on time

---
Other informations :
- [Screenshots](doc/SCREENSHOTS.md)
- [Detailed Features](doc/FEATURES.md)
- [Hardware requirements](doc/REQUIREMENTS.md)
- [Shell commands](doc/SHELL.md)
- [Text editor manual](doc/EDITOR.md)
- [Battery mode](doc/BATTERY.md)
- [Installation manual](doc/CAMFLASHER.md)
- [Build firmware](doc/FIRMWARE.md)
- [Project tree](doc/DIRECTORIES.md)


- [Library documentation : ](https://htmlpreview.github.io/?https://raw.githubusercontent.com/remibert/pycameresp/main/doc/lib/index.html)
	- [Homekit](doc/HOMEKIT.md)
	- [Html template](https://htmlpreview.github.io/?https://raw.githubusercontent.com/remibert/pycameresp/main/doc/lib/htmltemplate/index.html)
	- [Motion detection](https://htmlpreview.github.io/?https://raw.githubusercontent.com/remibert/pycameresp/main/doc/lib/motion/index.html)
	- [Servers](https://htmlpreview.github.io/?https://raw.githubusercontent.com/remibert/pycameresp/main/doc/lib/server/index.html) 
	- [Shell](https://htmlpreview.github.io/?https://raw.githubusercontent.com/remibert/pycameresp/main/doc/lib/shell/index.html)
	- [Camera](https://htmlpreview.github.io/?https://raw.githubusercontent.com/remibert/pycameresp/main/doc/lib/video/index.html)
	- [Web pages](https://htmlpreview.github.io/?https://raw.githubusercontent.com/remibert/pycameresp/main/doc/lib/webpage/index.html)
	- [Wifi](https://htmlpreview.github.io/?https://raw.githubusercontent.com/remibert/pycameresp/main/doc/lib/wifi/index.html)
