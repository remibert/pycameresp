# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" These classes are used to manage mqtt client """
# pylint:disable=consider-using-f-string
import tools.jsonconfig
import tools.logger

class MqttConfig(tools.jsonconfig.JsonConfig):
	""" Configuration of the mqtt client """
	def __init__(self):
		""" Constructor """
		tools.jsonconfig.JsonConfig.__init__(self)

		# Indicates if the presence detection is activated
		self.activated = False

		# Host name or ip address of mqtt broker
		self.host = b""

		# Port of mqtt broker
		self.port = 1883

		# User name of mqtt broker
		self.username = b""

		# Password of mqtt broker
		self.password = b""

class MqttClientInstance(tools.tasking.ClientInstance):
	""" Mqtt client instance """
	def __init__(self, **kwargs):
		tools.tasking.ClientInstance.__init__(self, **kwargs)

	def start(self):
		""" Start mqtt client """
		MqttClient.init()
		MqttClient.protocol.start(**self.kwargs)
		return "MqttClient",self.kwargs.get("mqtt_port", MqttClient.config.port)

class MqttClient:
	""" Mqtt client class """
	protocol = None
	config = None

	@staticmethod
	def init():
		""" Initialize mqtt client protocol """
		if MqttClient.config is None:
			MqttClient.config = MqttConfig()
			MqttClient.config.load_create()
		else:
			MqttClient.config.refresh()
		if MqttClient.config.activated:
			if MqttClient.protocol is None:
				from server.mqttprotocol import MqttProtocol
				MqttClient.protocol = MqttProtocol
			return True
		return False

	@staticmethod
	async def send(message):
		""" Low level mqtt message sender """
		MqttClient.init()
		if MqttClient.config.activated:
			return await MqttClient.protocol.send(message)

	@staticmethod
	def add_topic(**kwargs):
		""" Subscribe topic with decorator
		Parameters :
		 - topic : topic name
		 - qos : quality of service
		 - callback : callback called on publication """
		def add_topic(callback):
			MqttClient.init()
			kwargs["callback"] = callback
			MqttClient.protocol.add_topic(**kwargs)
			return callback
		return add_topic

	@staticmethod
	async def unsubscribe(**kwargs):
		""" Unsubscribe topic 
		Parameters :
		 - topic : topic name
		"""
		result = False
		MqttClient.init()
		if MqttClient.config.activated:
			result = await MqttClient.protocol.unsubscribe(**kwargs)
		return result

	@staticmethod
	async def subscribe(**kwargs):
		""" Subscribe topic 
		Parameters :
		 - topic : topic name
		  - qos : quality of service
		 - callback : callback called on publication
		"""
		result = False
		MqttClient.init()
		if MqttClient.config.activated:
			result = await MqttClient.protocol.subscribe(**kwargs)
		return result

	@staticmethod
	async def publish(**kwargs):
		""" Publish topic with its value 
		Parameters :
		 - topic : topic name
		 - value : value to publish
		 - qos : quality of service
		"""
		result = False
		MqttClient.init()
		if MqttClient.config.activated:
			result = await MqttClient.protocol.publish(**kwargs)
		return result

	@staticmethod
	def start(**kwargs):
		""" Start the mqtt client 
		mqtt_host  : mqtt broker ip address (string)
		mqtt_port  : mqtt broker port (int)
		keep_alive : the keep alive is a time interval measured in seconds (int)
		username   : user name (string)
		password   : password (string)
		debug      : True for see debug information (bool)
		dump       : show the content of exchange
		"""
		MqttClient.config = MqttConfig()
		MqttClient.config.load_create()
		if MqttClient.config.activated:
			tools.tasking.Tasks.create_client(MqttClientInstance(**kwargs))
		else:
			tools.logger.syslog("Mqtt client disabled in config")
