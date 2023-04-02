# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Sample of mqtt client. Support MQTT 3.11 """
from server.mqttclient import MqttClient
from tools import strings

@MqttClient.subscribe('testtopic')
async def on_topic(message, **kwargs):
	""" Example of the mqtt subscription
	to test publish : 
		mosquitto_pub -h 192.168.1.28 -p 1883 -t testtopic -u username -P password -q 2 -m "my test topic" """
	print("on_topic called  %s"%strings.tostrings(message.value))

@MqttClient.subscribe('forward_message')
async def on_forward_message(message, **kwargs):
	"""Example of the mqtt subscription with emission of a message
	To test subscribe :
		mosquitto_sub -h 192.168.1.28 -p 1883 -t receive_message -u username -P password
	To test publish :
		mosquitto_pub -h 192.168.1.28 -p 1883 -t forward_message -u username -P password -q 2 -m "Hello world" """
	print("on_forward_message  %s"%strings.tostrings(message.value))
	await MqttClient.publish(topic="receive_message", value=message.value)

def mqtt_test(loop, **kwargs):
	""" Sample mqtt test code
	Parameters :
		loop       : asynchronous loop
		host       : mqtt broker ip address (string)
		port       : mqtt broker port (int)
		keep_alive : the keep alive is a time interval measured in seconds (int)
		username   : user name (string)
		password   : password (string)
		debug      : True for see debug information (bool)
	
	Example :
		mqtt_test(host="192.168.1.28", port=1883, keep_alive=120, username="username", password="password", debug=True)
	"""
	# Example to open mqtt client
	MqttClient.start(**kwargs)
