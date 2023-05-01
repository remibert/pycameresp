# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Class to manage wifi and access point """
import sys
if sys.platform == "rp2":
    AUTHMODE = {0: b"open", 0x00200002: b"WPA-PSK", 0x00400004: b"WPA2-PSK", 0x00400006: b"WPA/WPA2-PSK"}
    AUTHMODE_DEFAULT = 0x00400004
else:
    AUTHMODE = {0: b"open", 1: b"WEP", 2: b"WPA-PSK", 3: b"WPA2-PSK", 4: b"WPA/WPA2-PSK"}
    AUTHMODE_DEFAULT = 3
