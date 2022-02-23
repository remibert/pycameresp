[Main page](/README.md) | [CamFlasher](/doc/CAMFLASHER.md)

# Battery mode for ESP32CAM

This operating mode allows you to place an ESP32CAM on battery, and to wake it up with a PIR sensor.
It is important to specify that the waking of the ESP32CAM, and the start of micropython, camera takes a fifteen seconds, it is then possible to miss motion images.

**Be careful, the battery mode activations produces deep sleeps, and all the servers are no longer accessible. Only activate it if you know what you are doing.**

To be able to operate the ESP32CAM on battery, some hardware modifications are required.

## Battery level detection
The **GPIO 12** is used to detect the battery level. The voltage must not be greater than 1.5V otherwise it will no longer boot.

A 100k(on +) connected to 50k (on gnd) resistor between the battery connector, and take the middle of resistor to connect it to the GPIO 12.

You need to calibrate the ADC values to 4.2v (100%) and 3.85v (0%) in web configuration page.

## PIR sensor
PIR detection connected on the **GPIO 13**, I use the SR602. 
With the SR602 you have to extend the detection delay (10s > boot time ESP32CAM) otherwise you lost the state (adding 90k resistor, see specification of SR602).

## Limit the consumption of the ESP32CAM on battery
In deep sleep mode, the AMS1117 regulator consumes 10mA, if you want your batteries not to drain too quickly,
you have to use an external LDO regulator 3.3V (in my case 6206A) and remove AMS1117 of the ESP32CAM (powered by 3.3 v it still consumes 4ma).
Then the consumption is close to 1.7mA with the SR602. 
To go even further, look here https://time4ee.com/articles.php?article_id=126


## Reduce the browout reset
To avoid reset brownout, you must add a 2200uF capacitor on 3.3v.

## Battery
Take 2 or more 18650 battery in parallel to avoid brownouts reset. 


