# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" These classes are used to manage mqtt client """
# pylint:disable=consider-using-f-string
from tools import jsonconfig, logger

class MqttConfig(jsonconfig.JsonConfig):
	""" Configuration of the mqtt client """
	def __init__(self):
		""" Constructor """
		jsonconfig.JsonConfig.__init__(self)

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
		""" Send message """
		MqttClient.init()
		if MqttClient.config.activated:
			return await MqttClient.protocol.send(message)

	@staticmethod
	def subscribe(topic, **kwargs):
		""" Subscribe callback on topic decorator """
		def subscribe(function):
			MqttClient.init()
			if MqttClient.config.activated:
				MqttClient.protocol.subscribe(topic, function, **kwargs)
			return function
		return subscribe

	@staticmethod
	def unsubscribe(topic):
		""" Unsubscribe topic name """
		MqttClient.init()
		if MqttClient.config.activated:
			MqttClient.protocol.unsubscribe(topic)

	@staticmethod
	async def publish(topic, value, **kwargs):
		""" Publish topic with its value """
		MqttClient.init()
		if MqttClient.config.activated:
			await MqttClient.protocol.publish(topic, value, **kwargs)

	@staticmethod
	def start(**kwargs):
		""" Start the mqtt client """
		MqttClient.init()
		if MqttClient.config.activated:
			MqttClient.protocol.start(**kwargs)
		else:
			logger.syslog("Mqtt client disabled in config")
