[Main page](/README.md) | [CamFlasher](/doc/CAMFLASHER.md)

# Micropython firmware

It is embedded in an improved [micropython](http://micropython.org) firmware. This platform starts automatically after writing the firmware. It works perfectly also on esp32 spiram without camera, and also esp32 without spiram but with more limitation.

# Build firmware for specific board

The build command must be used to get micropython source, patch source, build and install required tools.

The build.py script work on a Debian 11 distribution, however they ask when running to install certain tools, so you will have to enter the super user password.

Help of this command :

	usage: build.py [-h] [-i] [-g] [-d] [-p] [-b] [-a] [-c] [-o OUTPUTDIR] [boards [boards ...]]

	positional arguments:

		boards                Select boards to build micropython firmwares, for all firmwares use "*"

	optional arguments:

		-h, --help            show this help message and exit
		-i, --install         install the tools required to build the firmware
		-g, --get             get micropython source from git
		-d, --doc             build pycameresp html documentation
		-p, --patch           patch micropython sources with pycameresp patch
		-b, --build           build selected firmwares
		-a, --all             install tools, get source, patch, and build selected firmwares
		-c, --clean           clean micropython sources to remove all patch
		-s, --s3              build Esp32 S3 without problem
		-o OUTPUTDIR, --outputdir OUTPUTDIR                    output directory

The first time use command (get source, install required software and build firmware) : 
- **python3 build.py --all "ESP32CAM"** 

And after juste for rebuild use command :
- **python3 build.py --patch --build "ESP32CAM"**

Replace **ESP32CAM** by your prefered firmware, add double quote if you want to use wildcards for build many firmwares, for example ESP32 GENERIC SPIRAM :
- **python3 build.py --patch --build "GENERIC_SPIRAM"** 

Or for all ESP32 S2
- **python3 build.py --patch --build "ESP32CAM" "GENERIC_SPIRAM"** 

To build ESP32 S3 you must clean all and add option --s3  :
- **python3 build.py --clean --s3 --patch --build "GENERIC_S3_SPIRAM"**

