Pycameresp is originally designed to be a completely standalone motion detector on ESP32-CAM, but all servers and other functionality also work on generic Esp32 and Pico PI, Pico PI W.

---
The following features are available on all Esp32 and Pico Pi :

 - WiFi network management with configuration via web interface. 
 - Automatic Wifi connection and reconnection in case of deconnection.
 - All servers running simultaneously (FTP, HTTP, Telnet) and password protected.
 - Notifications can be sent to smartphone.
 - Web interface for installation, configuration, consultation.
 - Periodic time adjustment with NTP synchronization.
 - Recording activities and errors in the rotating log file.
 - Remote maintenance using telnet and built-in shell.
 - Built-in text editor with syntax highlighting capable of executing scripts directly from the board.

The following features are available on Esp32 with camera for motion detection :
- Live video stream of camera
- Detection of house inhabitants smartphones for automatic activation/deactivation of motion detection.
- Consultation and configuration of motion detections from the web interface.
- Space management available on the sdcard.
- Notification on smartphone of motion detection with sending of the captured image.

The firmware is based on an improved version of [micropython](http://micropython.org), it is ready to use, because all pycameresp modules are embedded in the firmware.

The start of pycameresp is in the main.py, and therefore fully modifiable.

The focus is on reducing RAM consumption and reliability, 
the entire platform can operates several months without requiring humain intervention.

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
	- [Html template](https://htmlpreview.github.io/?https://raw.githubusercontent.com/remibert/pycameresp/main/doc/lib/htmltemplate/index.html)
	- [Motion detection](https://htmlpreview.github.io/?https://raw.githubusercontent.com/remibert/pycameresp/main/doc/lib/motion/index.html)
	- [Servers](https://htmlpreview.github.io/?https://raw.githubusercontent.com/remibert/pycameresp/main/doc/lib/server/index.html) 
	- [Shell](https://htmlpreview.github.io/?https://raw.githubusercontent.com/remibert/pycameresp/main/doc/lib/shell/index.html)
	- [Camera](https://htmlpreview.github.io/?https://raw.githubusercontent.com/remibert/pycameresp/main/doc/lib/video/index.html)
	- [Web pages](https://htmlpreview.github.io/?https://raw.githubusercontent.com/remibert/pycameresp/main/doc/lib/webpage/index.html)
	- [Wifi](https://htmlpreview.github.io/?https://raw.githubusercontent.com/remibert/pycameresp/main/doc/lib/wifi/index.html)
