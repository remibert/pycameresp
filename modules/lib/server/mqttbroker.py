# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Mqtt broker management class """
import server.server
import tools.logger
import tools.tasking

class MqttBrokerInstance(tools.tasking.ServerInstance):
	""" Mqtt broker instance """
	BrokerCoreClass = None
	def __init__(self, **kwargs):
		tools.tasking.ServerInstance.__init__(self, **kwargs)

	async def on_connection(self, reader, writer):
		""" Asynchronous connection detected """
		try:
			if MqttBrokerInstance.BrokerCoreClass is None:
				tools.logger.syslog("MqttBroker load")
				from server.mqttbrokercore import MqttBrokerCore
				MqttBrokerInstance.BrokerCoreClass = MqttBrokerCore
				tools.logger.syslog("MqttBroker ready")
			if MqttBrokerInstance.BrokerCoreClass is not None:
				MqttBrokerInstance.BrokerCoreClass(reader, writer)
		except Exception as err:
			tools.logger.syslog(err)

class MqttBroker:
	""" Mqtt server instance """
	config = None

	@staticmethod
	def init():
		""" Initialize mqtt server """
		if MqttBroker.config is None:
			MqttBroker.config = server.server.ServerConfig()
			MqttBroker.config.load_create()
		else:
			MqttBroker.config.refresh()

	@staticmethod
	def start(**kwargs):
		""" Start the mqtt server with asyncio loop.
		broker_port : tcp/ip mqtt port of the server default 1883  """
		MqttBroker.init()
		if MqttBroker.config.mqtt_broker:
			kwargs["port"] = kwargs.get("mqtt_broker_port",1883)
			kwargs["name"] = "MqttBroker"
			tools.tasking.Tasks.create_server(MqttBrokerInstance(**kwargs))
		else:
			tools.logger.syslog("MqttBroker disabled in config")
