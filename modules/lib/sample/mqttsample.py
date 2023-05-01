# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Sample of mqtt client. Support MQTT 3.11 """
import server.mqttclient
import tools.strings

@server.mqttclient.MqttClient.add_topic(topic='testtopic')
async def on_topic(message, **kwargs):
	""" Example of the mqtt subscription

	to test publish : 
		mosquitto_pub -h $BROKER -p 1883 -t testtopic -u username -P password -q 2 -m "my test topic" """
	print("on_topic called  %s"%tools.strings.tostrings(message.value))

@server.mqttclient.MqttClient.add_topic(topic='forward_message')
async def on_forward_message(message, **kwargs):
	""" Example of the mqtt subscription with emission of a message

	to test subscribe :
		mosquitto_sub -h $BROKER -p 1883 -t receive_message -u username -P password

	to test publish :
		mosquitto_pub -h $BROKER -p 1883 -t forward_message -u username -P password -q 2 -m "Hello world" """
	print("on_forward_message  %s"%tools.strings.tostrings(message.value))
	await server.mqttclient.MqttClient.publish(topic="receive_message", value=message.value)

@server.mqttclient.MqttClient.add_topic(topic='command')
async def on_command(message, **kwargs):
	""" Example of to test dynamic subscribe, unsubscribe
	to test dynamic subscribe :
		mosquitto_pub -h $BROKER -p 1883 -t command -u username -P password -m "subscribe test"
	
	to test dynamic unsubscribe :
		mosquitto_pub -h $BROKER -p 1883 -t command -u username -P password -m "unsubscribe test"

	to test publish reception :
		mosquitto_pub -h $BROKER -p 1883 -t test -u username -P password -m "hello world"
	"""
	async def on_test(message, **kwargs):
		print("On test called with message=",message.value)

	command, param = tools.strings.tostrings(message.value).split(" ")
	if command =="subscribe":
		await server.mqttclient.MqttClient.subscribe(topic=param, callback=on_test)
	elif command == "unsubscribe":
		await server.mqttclient.MqttClient.unsubscribe(topic=param)
