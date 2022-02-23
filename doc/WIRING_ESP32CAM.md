[Main page](/README.md) | [CamFlasher](/doc/CAMFLASHER.md)

# Specific wiring for esp32cam

The ESP32-CAM does not have a usb connection, you have to add a usb/serial converter :

![Esp32camProgram.png](/images/Esp32camProgram.png "Esp32Cam flash firmware wiring")

Put jumper on GPIO 0 to GND for programming the firmware.
Remove it once the firmware has been programmed, press reset button after.

