[Main page](/README.md) | [CamFlasher](/doc/CAMFLASHER.md)

# Micropython firmware

It is embedded in an improved [micropython](http://micropython.org) firmware. This platform starts automatically after writing the firmware. It works perfectly also on esp32 spiram without camera, and also esp32 without spiram but with more limitation.

Most scripts work on Osx or Linux, I personally use "Visual Studio Code", with python plugins for debugging. 
Of course, in this case the code specific to the camera or to the ESP32 is simulated (see simul directory).

The first time I had a lot of trouble rebuilding micropython, I ended up creating scripts to make the job easier.

These scripts work on a linux kubuntu distribution, however they ask when running to install certain tools, so you will have to enter the super user password.

To generate firmware for ESP32CAM, ESP32_SPIRAM, ESP32_GENERIC, you need to run in order.

- **getFirmware.sh** : Get the gits sources, install the necessary tools, position on the right tag
- **patchCFirmware.sh** : Apply the patch on the C micropython and esp32 sources. This fixes some problem, and it adds missing functionality.
- **patchPythonFirmware.sh** : Patch the micropython firmware with python scripts, this makes it possible to embed all the scripts of this project in the firmware, and to accelerate the loading time and reduce memory occupation.
- **buildAllFirmware.sh** : Build the three firmware for the ESP32CAM, ESP32_SPIRAM, ESP32_GENERIC. All firmwares are placed in the firmware directory.
- **buildDoc.sh** : Build the documentation, requires the installation of pdoc3.
- **buildFirmware.sh** : Build one firmware, you must specifie the name (ESP32CAM,GENERIC,GENERIC_SPIRAM)

If you don't want to embed the python scripts in the firmware, just don't run the command patchPythonFirmware.sh.

