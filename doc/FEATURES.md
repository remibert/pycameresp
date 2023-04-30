[Main page](/README.md) | [CamFlasher](/doc/CAMFLASHER.md)

# Features

Below is the list of features supported by the software

- Wifi manager :
	- Manages wifi loss, and reconnects automatically
	- Manage several wifi networks
	- Fallback to access point if no known wifi networks

- Servers :
	- HTTP web server
	- FTP server
	- Telnet server
	- User, password for all servers

- Clients :
	- NTP synchronization periodicaly (always on time)
	- <a href="https://pushover.net">Push over</a> for smartphone notification with image attached
	- Ping
	- Light DNS request
	- Wan ip getting
	- Smartphone presence detection on network

- Web pages
	- Board informations
	- Wifi network and access point configuration
	- User and password initialisation
	- Server activation
	- <a href="https://pushover.net">Push over</a> configuration
	- Battery configuration
	- Presence detection configuration
	- Wake up periodic configuration

- Battery monitoring
	- Manage battery level
	- Protects the battery if the level is too low

- Tools executable directly on the board :
	- Syntax highlight text editor, with possibility to execute script directly in device
	- Shell (cd, pwd, cat, mkdir, mv, cp, rm, ls, find, grep, edit, man, ping, ...)
	- Html template engine using <a href="https://jquery.com">jquery</a>, <a href="https://www.w3schools.com/bootstrap5">bootstrap 5</a>
	- Error logging in syslog file with rotation

- Miscellaneous functionality :
	- Crash protection with watchdog
	- Monitoring of task execution
	- Force reboot if too frequent problem detected or on exit of main loop

- Micropython firmware patch :
	- Adding reset cause Brownout
	- Embedding all python scripts in the firmware (fast loading time, drastic reduction in ram consumption)

- Micropython ESP32CAM firmware specificities :
	- Full camera support by micropython
	- Motion detection
	- Web page motion configuration
	- Web page to view motion detection history
	- Web page camera streaming
	- Management of space on the sd card (automatic cleaning of old data)
	- Board with camera supported : ESP32-CAM, ESP32-CAM-MB, ESP32ONE, M5Stack Camera

With the exception of boards with camera, which require a driver in micropython firmware, all python scripts can run on a standard version of micropython.

For cards with little ram memory, it can be necessary to compile the firmware that embeds pycameresp : when all the python scripts are in ROM, they consume very little RAM.