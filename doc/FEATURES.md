[Main page](/README.md) | [CamFlasher](/doc/CAMFLASHER.md)

# Features

Below is the list of features supported by the software

- Servers :
	- HTTP web server
	- FTP server
	- Telnet server
	- Login, password can be defined for servers
	- Homekit server

- Clients :
	- NTP synchronization
	- <a href="https://pushover.net">Push over</a> notification with image sent to smartphone
	- Ping and light DNS request
	- Getting Wan Ip

- Web interface
	- Board informations
	- Wifi configuration
	- Access point configuration
	- Server activation
	- User and password initialisation
	- <a href="https://pushover.net">Push over</a> configuration
	- Battery mode configuration

- Tools on the boards :
	- VT100 text editor with python script execution
	- Shell (cd, pwd, cat, mkdir, mv, cp, rm, ls, find, grep, edit, man, ...)
	- Html template engine using <a href="https://jquery.com">jquery</a>, <a href="https://www.w3schools.com/bootstrap4">bootstrap 4</a>

- Micropython firmware patch :
	- Support ADC for GPIO 0,2,4,12,13,14,15,25,26,27
	- Support NVS set, get, erase added
	- Adding reset cause Brownout
	- Embedding all scripts of this software (Faster loading times, reduce RAM footprint)

- Micropython ESP32CAM firmware specificities :
	- Full camera support by micropython
	- Motion detection
	- Presence detection
	- Web motion configuration
	- Web presence configuration
	- Web camera streaming

Ftp, Http, Motion detection works simultaneously, it uses asyncio mechanisms.
However, during camera streaming, motion detection is suspended to have enough frames per second.


