# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
# pylint:disable=consider-using-f-string
# pylint:disable=unspecified-encoding
# pylint:disable=consider-using-f-string
""" Mqtt server implementation core class """
# export BROKER=192.168.1.25;mosquitto_sub -h $BROKER -p 1883 -t receive_message -u username -P password -q 2
# export BROKER=192.168.1.25;d=$( { date; } 2>&1); mosquitto_pub -h $BROKER -p 1883  -u username -P password -t forward_message -m $d -q 1  --repeat 10 -r
import uasyncio
import server.stream
import server.user
import server.mqttmessages
import tools.logger
import tools.fnmatch
import tools.filesystem
import tools.strings
import tools.date
import tools.tasking

class MqttRetainPublication:
	""" Class to store publication retained """
	def __init__(self, topic , value, qos, dup, retain, identifier):
		self.topic = topic
		self.value = value
		self.qos   = qos
		self.dup   = dup
		self.retain = retain
		self.identifier = identifier

class MqttBrokerCore:
	""" Mqtt implementation server core """
	clients = []
	retains = {}
	client_id = [0]

	def __init__(self, reader, writer):
		""" Mqtt constructor method """
		self.client = server.stream.Stream(reader, writer)
		self.remoteaddr = tools.strings.tobytes(self.client.writer.get_extra_info('peername')[0])
		self.keep_alive = 60
		self.subscriptions = set()
		self.publications = []
		MqttBrokerCore.client_id[0] += 1
		self.client_id = MqttBrokerCore.client_id[0]

		tools.tasking.Tasks.create_task(self.main_task())
		self.quit = False
		self.on_commands = {
			server.mqttmessages.MqttDisconnect  : self.on_disconnect,
			server.mqttmessages.MqttPingReq     : self.on_ping_req,
			server.mqttmessages.MqttPublish     : self.on_publish,
			server.mqttmessages.MqttPubAck      : self.on_pub_ack,
			server.mqttmessages.MqttPubComp     : self.on_pub_comp,
			server.mqttmessages.MqttPubRel      : self.on_pub_rel,
			server.mqttmessages.MqttPubRec      : self.on_pub_rec,
			server.mqttmessages.MqttSubscribe   : self.on_subscribe,
			server.mqttmessages.MqttUnsubscribe : self.on_unsubscribe,
		}

	async def on_connect(self, command):
		""" Connect command received """
		result = False
		# Check protocol version
		if command.protocol_level != 4 or command.protocol_name != "MQTT":
			return_code = server.mqttmessages.MQTT_CONNACK_UNACCEPTABLE_PROTOCOL
		# Check login password
		if server.user.User.check(tools.strings.tobytes(command.username), tools.strings.tobytes(command.password), activity=False):
			result = True
			return_code = server.mqttmessages.MQTT_CONNACK_ACCEPTED
		else:
			return_code = server.mqttmessages.MQTT_CONNACK_BAD_USER
		self.keep_alive = command.keep_alive

		response = server.mqttmessages.MqttConnAck(return_code=return_code)
		await response.write(self.client)
		return result

	async def on_disconnect(self, command):
		""" Disconnect command received """
		self.quit = True

	async def on_ping_req(self, command):
		""" Ping request received """
		response = server.mqttmessages.MqttPingResp()
		await response.write(self.client)

	async def on_pub_ack(self, command):
		""" Publish acknoledge received """
		for client in MqttBrokerCore.clients:
			await client.pub_ack(self, command)

	async def pub_ack(self, sender, command):
		""" Send publish ack """
		for publication in self.publications:
			if command.identifier == publication.identifier:
				self.publications.remove(publication)

	async def on_pub_comp(self, command):
		""" Publish complete received """
		for client in MqttBrokerCore.clients:
			await client.pub_comp(self, command)

	async def pub_comp(self, sender, command):
		""" Send publish complete """
		for publication in self.publications:
			if command.identifier == publication.identifier:
				response = server.mqttmessages.MqttPubComp(identifier=command.identifier)
				await response.write(self.client)
				self.publications.remove(publication)

	async def on_pub_rel(self, command):
		""" Publish release received """
		for client in MqttBrokerCore.clients:
			await client.pub_rel(self, command)

	async def pub_rel(self, sender, command):
		""" Send publish rec """
		for publication in self.publications:
			if command.identifier == publication.identifier:
				response = server.mqttmessages.MqttPubRel(identifier=command.identifier)
				await response.write(self.client)

	async def on_pub_rec(self, command):
		""" Publish received """
		for client in MqttBrokerCore.clients:
			await client.pub_rec(self, command)

	async def pub_rec(self, sender, command):
		""" Send publish rec """
		for publication in self.publications:
			if command.identifier == publication.identifier:
				response = server.mqttmessages.MqttPubRec(identifier=command.identifier)
				await response.write(self.client)

	def treat_retain(self, command):
		""" Manage message retain """
		# If erase message retained required
		if len(command.value) == 0:
			if command.topic in MqttBrokerCore.retains:
				del MqttBrokerCore.retains[command.topic]
		# If message must be replaced
		elif command.retain and len(command.value) > 0:
			MqttBrokerCore.retains[command.topic] = MqttRetainPublication(
				command.topic,
				command.value,
				command.qos,
				command.dup,
				command.retain,
				command.identifier if command.qos > server.mqttmessages.MQTT_QOS_ONCE else None)

	async def on_publish(self, command):
		""" Publish topic for all clients connected """
		if command.qos > server.mqttmessages.MQTT_QOS_ONCE:
			self.publications.append(command)

		self.treat_retain(command)

		if command.qos == server.mqttmessages.MQTT_QOS_LEAST_ONCE:
			response = server.mqttmessages.MqttPubAck(identifier=command.identifier)
			await response.write(self.client)

		for client in MqttBrokerCore.clients:
			await client.publish(self, command)

	async def publish(self, sender, command):
		""" Publish topic for client connected """
		for subscription in self.subscriptions:
			if subscription == command.topic:
				forward = server.mqttmessages.MqttPublish(
					topic=command.topic,
					value=command.value,
					qos  =command.qos,
					dup  =command.dup,
					retain=command.retain,
					identifier= command.identifier if command.qos > server.mqttmessages.MQTT_QOS_ONCE else None)
				if command.qos > server.mqttmessages.MQTT_QOS_ONCE:
					self.publications.append(forward)
				await forward.write(self.client)

	async def on_subscribe(self, command):
		""" Subscribe command received """
		return_codes = []

		# Check subscription
		for topic, qos in command.topics:
			if qos > server.mqttmessages.MQTT_QOS_EXACTLY_ONCE:
				tools.logger.syslog("MqttBroker bad protocol %s"%tools.strings.tostrings(self.remoteaddr))
				self.quit = True
			else:
				return_codes.append(qos)
			self.subscriptions.add(topic)
		response = server.mqttmessages.MqttSubAck(return_code=return_codes)
		await response.write(self.client)

		# Treat retain topics
		for topic, qos in command.topics:
			retain = MqttBrokerCore.retains.get(topic, None)
			if retain:
				publish = server.mqttmessages.MqttPublish(
					topic =retain.topic,
					value =retain.value,
					qos   =retain.qos,
					dup   =retain.dup,
					retain=retain.retain)
				await publish.write(self.client)
				if retain.qos > server.mqttmessages.MQTT_QOS_ONCE:
					self.publications.append(publish)

	async def on_unsubscribe(self, command):
		""" Unsubscribe command received """
		for topic in command.topics:
			for subscription in self.subscriptions:
				if subscription == topic:
					self.subscriptions.remove(subscription)
					break
		response = server.mqttmessages.MqttUnSubAck()
		await response.write(self.client)

	async def main_task(self):
		""" Main mqtt broker task, treat all commands received """
		try:
			tools.logger.syslog("MqttBroker connected %s"%tools.strings.tostrings(self.remoteaddr))

			# Wait connect message
			command = await uasyncio.wait_for(server.mqttmessages.MqttMessage.receive(self.client), timeout = self.keep_alive + self.keep_alive//2)
			if isinstance(command, server.mqttmessages.MqttConnect):

				# Treat connect message
				if await self.on_connect(command):
					tools.logger.syslog("MqttBroker established %s"%tools.strings.tostrings(self.remoteaddr))
					try:
						# Enter in broker management loop
						MqttBrokerCore.clients.append(self)
						while self.quit is False:
							command = await uasyncio.wait_for(server.mqttmessages.MqttMessage.receive(self.client), timeout = self.keep_alive + self.keep_alive//2)
							# If command failed
							if command is None:
								self.quit = True
							else:
								found = False
								# Search the command treatment callback
								for classe, on_command in self.on_commands.items():
									if isinstance(command, classe):
										await on_command(command)
										found = True
										break

								if found is False:
									tools.logger.syslog("MqttBroker unknown command %s"%tools.strings.tostrings(self.remoteaddr))
					finally:
						MqttBrokerCore.clients.remove(self)

		except uasyncio.CancelledError as err:
			tools.logger.syslog("MqttBroker cancelled %s"%tools.strings.tostrings(self.remoteaddr))
		except uasyncio.TimeoutError as err:
			tools.logger.syslog("MqttBroker ping timeout %s"%tools.strings.tostrings(self.remoteaddr))
		except Exception as err:
			tools.logger.syslog(err)
		finally:
			await self.client.close()
			tools.logger.syslog("MqttBroker disconnected %s"%tools.strings.tostrings(self.remoteaddr))
