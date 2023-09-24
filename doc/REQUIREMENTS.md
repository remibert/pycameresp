[Main page](/README.md) | [CamFlasher](/doc/CAMFLASHER.md)

# Requirements

Micropython on ESP32 does not leave much space in RAM, a SPIRAM is recommended, but the platform can however work, it is then necessary to limit the number of servers used. In the version without spiram, micropython leaves 103 kb, which is extremely little to run a platform like this. In this case to limit RAM consumption, you must edit the main.py, and replace the "=True", with "=False", on all the unwanted functionalities.

For motion capture you absolutely need an ESP32CAM or FREENOVE CAM S3.

# Devices supported

Below are the devices compatible with pycameresp :

![ESP32CAM](/images/Device_ESP32CAM.jpg "ESP32CAM")
![ESP32CAM-MB](/images/Device_ESP32CAM-MB.jpg "ESP32CAM-MB")
![TTGO](/images/Device_TTGO.jpg "TTGO")
![ESP32ONE](/images/Device_ESP32ONE.jpg "ESP32ONE")
![M5StackCamera](/images/Device_M5StackCamera.jpg "M5StackCamera")
![BPI-Leaf-S3](/images/Device_BPI-Leaf-S3.png "BPI-Leaf-S3")

![NODEMCU](/images/Device_NODEMCU.jpg "NODE MCU")
![LOLIN32](/images/Device_LOLIN32.jpg "LOLIN32")
![PicoPi](/images/Device_PicoPi.png "Pico PI W")
![Freenove CAM S3](/images/Device_FREENOVE_CAM_S3.png "Freenove CAM S3")

Note on the freenove cam S3, I had problems with wifi disruption, which limited the video streaming speed, to correct this I unsoldered the two connectors from the edges of the card, it's tedious, but the speed has become maximum.