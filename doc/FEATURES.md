[Main page](/README.md) | [CamFlasher](/doc/CAMFLASHER.md)

# Features

Below is the list of features supported by the software

- Network :
	- Wifi configuration
	- Wifi manager
	- Manages automatic reconnection
	- Can connect to several wifi
- Servers :
	- HTTP web server
	- FTP server
	- Telnet server
	- Login, password can be defined for servers

- Clients :
	- NTP synchronization
	- <a href="https://pushover.net">Push over</a> notification with image sent to smartphone
	- Ping and light DNS request
	- Getting Wan Ip

- Web interface
	- Board informations
	- Access point configuration
	- Server activation
	- User and password initialisation
	- <a href="https://pushover.net">Push over</a> configuration
	- Battery mode configuration

- Tools on the boards :
	- Text editor with syntax highlight, python script execution directly in device
	- Shell (cd, pwd, cat, mkdir, mv, cp, rm, ls, find, grep, edit, man, ...)
	- Html template engine using <a href="https://jquery.com">jquery</a>, <a href="https://www.w3schools.com/bootstrap4">bootstrap 4</a>

- Micropython firmware patch :
	- Adding reset cause Brownout
	- Embedding all scripts of this software (Faster loading times, considerably reduces ram consumption compared to an installation of .py)

- Micropython ESP32CAM firmware specificities :
	- Full camera support by micropython
	- Motion detection
	- Presence detection
	- Web motion configuration
	- Web presence configuration
	- Web camera streaming

Ftp, Http, Motion detection works simultaneously, it uses asyncio mechanisms.
However, during camera streaming, motion detection is suspended to have enough frames per second.


