# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Allows you to activate/deactivate features from main.py """
import tools.jsonconfig
import tools.filesystem


class FeaturesConfig(tools.jsonconfig.JsonConfig):
	""" Features configuration """
	def __init__(self, **kwargs):
		tools.jsonconfig.JsonConfig.__init__(self)
		self.plugin       = kwargs.get("plugin",      False) # Start all plugins (must be contains lib/plugins/*/__startup__.py)
		self.awake        = kwargs.get("awake",       False) # Awake and deepsleep periodically task
		self.battery      = kwargs.get("battery",     False) # Battery level manager task
		self.shell        = kwargs.get("shell",       False) # Shell with text editor task
		self.wifi         = kwargs.get("wifi",        False) # Wifi manager task
		self.ftp          = kwargs.get("ftp",         False) # Ftp server task
		self.http         = kwargs.get("http",        False) # Http server task
		self.telnet       = kwargs.get("telnet",      False) # Telnet server task
		self.ntp          = kwargs.get("ntp",         False) # Ntp synchronisation task
		self.wanip        = kwargs.get("wanip",       False) # Wanip periodically obtained task
		self.mqtt_broker  = kwargs.get("mqtt_broker", False) # Mqtt broker task
		self.mqtt_client  = kwargs.get("mqtt_client", False) # Mqtt client task
		self.webhook      = kwargs.get("webhook",     False) # Webhook notification task
		self.pushover     = kwargs.get("pushover",    False) # Pushover notification task
		self.presence     = kwargs.get("presence",    False) # Home occupant presence detection task
		self.camera       = kwargs.get("camera",      False) # Camera configuration
		self.motion       = kwargs.get("motion",      False) # Motion detection task
		self.log_size     = kwargs.get("log_size",32*1024)   # Log files size
		self.log_quantity = kwargs.get("log_quantity",4)     # Quantity of log file
		self.device       = kwargs.get("device","ESP32CAM")  # Default device name
		self.http_port    = kwargs.get("http_port",80)       # Default http port
		global features
		features = self

features = FeaturesConfig()
