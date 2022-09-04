# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class to manage wifi and access point """
import sys
from wifi.accesspoint import *
from wifi.station import *
from wifi.wifi import *
from wifi.ip import *

if sys.platform == "rp2":
    AUTHMODE = {0: b"open", 0x00200002: b"WPA-PSK", 0x00400004: b"WPA2-PSK", 0x00400006: b"WPA/WPA2-PSK"}
    AUTHMODE_DEFAULT = 0x00400004
else:
    AUTHMODE = {0: b"open", 1: b"WEP", 2: b"WPA-PSK", 3: b"WPA2-PSK", 4: b"WPA/WPA2-PSK"}
    AUTHMODE_DEFAULT = 3
