[Main page](/README.md) | [CamFlasher](/doc/CAMFLASHER.md)

# Homekit

This part requires the modified python firmware for esp32. 
If after testing, you can no longer see your homekit accessory, then it may be necessary to do a Homekit.eraseAll(), this destroys the current homekit accessory. With great regret, I did not get the camera to work at the same time as the homekit, it seems that there are difficulties to cohabit, due to not enough space of memory, to allocate process.

- [Library documentation](https://htmlpreview.github.io/?https://raw.githubusercontent.com/remibert/pycameresp/main/doc/lib/homekit/index.html)

- [Samples](https://github.com/remibert/pycameresp/tree/main/examples/homekit)
