# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class to manage wifi and access point """
# from wifi.hostname import *
from wifi.accesspoint import *
from wifi.station import *
from wifi.wifi import *

AUTHMODE = {0: b"open", 1: b"WEP", 2: b"WPA-PSK", 3: b"WPA2-PSK", 4: b"WPA/WPA2-PSK"}
