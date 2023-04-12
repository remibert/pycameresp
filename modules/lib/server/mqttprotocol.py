# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Support for mqtt client protocol using asynchronous sockets. Support MQTT 3.11 """
import uasyncio
import wifi.hostname
import server.mqttclient
import server.notifier
import server.mqttmessages
import tools.logger
import tools.strings
import tools.tasking

class MqttSubscription:
	""" Subscription callback caller """
	def __init__(self, topic, callback, **kwargs):
		""" Constructor """
		self.topic = topic
		self.kwargs  = kwargs
		self.callback = callback
		self.qos = kwargs.get("qos",server.mqttmessages.MQTT_QOS_ONCE)

	async def call(self, message):
		""" Call callback registered """
		await self.callback(message, **self.kwargs)

class MqttClientContext:
	""" Context of the mqtt client """
	def __init__(self, **kwargs):
		""" Constructor """
		config = server.mqttclient.MqttConfig()
		if config.load() is False:
			config.save()

		self.kwargs = kwargs
		self.kwargs["mqtt_host"]   = kwargs.get("mqtt_host",config.host)
		self.kwargs["mqtt_port"]   = kwargs.get("mqtt_port",config.port)
		self.kwargs["keep_alive"] = kwargs.get("keep_alive",60)
		if self.kwargs["keep_alive"] < 10:
			self.kwargs["keep_alive"] = 10
		self.keep_alive = self.kwargs["keep_alive"]
		self.kwargs["username"] = kwargs.get("username",config.username)
		self.kwargs["password"] = kwargs.get("password",config.password)
		self.streamio   = None
		self.state = MqttState.STATE_OPEN
		self.debug = kwargs.get("debug",False)
		self.kwargs["client_id"] = kwargs.get("client_id",wifi.hostname.Hostname().get_hostname())
		self.retry_count= 0

class MqttState:
	""" Mqtt protocol management state machine """	
	STATE_OPEN      = 1
	STATE_CONNECT   = 2
	STATE_CONNACK   = 3
	STATE_ACCEPTED  = 4
	STATE_REFUSED   = 5
	STATE_ESTABLISH = 6
	STATE_CLOSE     = 7
	STATE_WAIT      = 8

class MqttProtocol:
	""" Manages an mqtt client """
	subscriptions = {}
	controls = {}
	context = None
	publications = []

	@staticmethod
	def start(**kwargs):
		""" Start the mqtt client """
		if MqttProtocol.context is None:
			MqttProtocol.context = MqttClientContext(**kwargs)
			tools.tasking.Tasks.create_monitor(MqttStateMachine.task, **kwargs)
			tools.tasking.Tasks.create_monitor(MqttProtocol.ping_task, **kwargs)

	@staticmethod
	async def send(message):
		""" Send message """
		result = False
		if MqttProtocol.context is not None:
			if MqttProtocol.context.debug:
				print("Mqtt send    : %s"%message.__class__.__name__)
			try:
				await message.write(MqttProtocol.context.streamio)
				result = True
			except Exception as err:
				pass
		return result

	@staticmethod
	async def disconnect():
		""" Send diconnect message """
		if MqttProtocol.context.state == MqttState.STATE_ESTABLISH:
			await MqttProtocol.send(server.mqttmessages.MqttDisconnect())
			MqttProtocol.context.state = MqttState.STATE_CLOSE

	@staticmethod
	async def ping_task(**kwargs):
		""" Ping server periodicaly """
		if MqttProtocol.context.state == MqttState.STATE_ESTABLISH:
			await MqttProtocol.send(server.mqttmessages.MqttPingReq())
			await uasyncio.sleep(MqttProtocol.context.keep_alive)

			# Send another time publication if not acknowledged
			if len(MqttProtocol.publications) > 0:
				for publication in MqttProtocol.publications:
					if (publication.sent_time + MqttProtocol.context.keep_alive*500) < tools.strings.ticks():
						await MqttProtocol.send(publication)
						publication.dup = 1
		else:
			await uasyncio.sleep(MqttProtocol.context.keep_alive//2)

	@staticmethod
	def add_topic(**kwargs):
		""" Add a subscription to the topic decorator """
		callback = kwargs.get("callback",None)
		topic    = kwargs.get("topic", None)
		if callback and topic:
			MqttProtocol.subscriptions[tools.strings.tostrings(topic)] = MqttSubscription(**kwargs)
			return True
		return False

	@staticmethod
	def remove_topic(**kwargs):
		""" Remove a subscription to the topic """
		topic    = kwargs.get("topic", None)
		if topic:
			subscription = MqttProtocol.subscriptions.get(topic, None)
			if subscription:
				del MqttProtocol.subscriptions[topic]

	@staticmethod
	async def subscribe(**kwargs):
		""" Subscribe topic """
		result = True
		if MqttProtocol.context is not None:
			result = MqttProtocol.add_topic(**kwargs)
			if result:
				message = server.mqttmessages.MqttSubscribe(**kwargs)
				if MqttProtocol.context.state == MqttState.STATE_ESTABLISH:
					result = await MqttProtocol.send(message)
		else:
			result = False
		return result

	@staticmethod
	async def unsubscribe(**kwargs):
		""" Unsubscribe topic """
		result = True
		if MqttProtocol.context is not None:
			message = server.mqttmessages.MqttUnsubscribe(**kwargs)
			MqttProtocol.remove_topic(**kwargs)
			if MqttProtocol.context.state == MqttState.STATE_ESTABLISH:
				await MqttProtocol.send(message)
		else:
			result = False
		return result

	@staticmethod
	async def publish(**kwargs):
		""" Publish message on topic """
		result = True
		if MqttProtocol.context is not None:
			message = server.mqttmessages.MqttPublish(**kwargs)
			if message.qos != server.mqttmessages.MQTT_QOS_ONCE:
				MqttProtocol.publications.append(message)
			if MqttProtocol.context.state == MqttState.STATE_ESTABLISH:
				result = await MqttProtocol.send(message)
				message.dup = 1
		else:
			result = False
		return result

	@staticmethod
	async def call_subscription(message):
		""" Remove callback on subscription """
		subscription = MqttProtocol.subscriptions.get(tools.strings.tostrings(message.topic), (None,None,None))
		if subscription is not None:
			try:
				await subscription.call(message)
			except Exception as err:
				tools.logger.syslog(err)

	@staticmethod
	def add_control(control, **kwargs):
		""" Add a callback to control payload """
		def add_control(callback):
			MqttProtocol.controls[control] = (callback, kwargs)
			return callback
		return add_control

	@staticmethod
	def remove_control(control):
		""" Remove callback on control payload """
		control = MqttProtocol.controls.get(control, None)
		if control is not None:
			del MqttProtocol.controls[control]

	@staticmethod
	@server.notifier.Notifier.add()
	async def notify_message(notification):
		""" Notify message for mqtt """
		config = server.mqttclient.MqttConfig()
		if config.load() is False:
			config.save()

		result = True
		if config.activated or notification.forced:
			if notification.data:
				value = notification.data
			elif notification.value is not None and notification.value != "":
				value = notification.value
			elif notification.message is not None and notification.message != "":
				value = notification.message
			else:
				value = None

			if notification.topic and value:
				if MqttProtocol.notify_message not in notification.sent:
					topic = "%s/%s"%(tools.strings.tostrings(wifi.hostname.Hostname().get_hostname()), tools.strings.tostrings(notification.topic))
					result = await MqttProtocol.publish(topic=topic, value=value)
					if result is True:
						notification.sent.append(MqttProtocol.notify_message)
		return result

class MqttStateMachine:
	""" Mqtt protocol management state machine """	
	STATE_OPEN      = 1
	STATE_CONNECT   = 2
	STATE_CONNACK   = 3
	STATE_ACCEPTED  = 4
	STATE_REFUSED   = 5
	STATE_ESTABLISH = 6
	STATE_CLOSE     = 7
	STATE_WAIT      = 8

	@staticmethod
	async def state_open():
		""" Open mqtt state open socket """
		try:
			reader,writer = await uasyncio.open_connection(tools.strings.tostrings(MqttProtocol.context.kwargs.get("mqtt_host")), MqttProtocol.context.kwargs.get("mqtt_port"))
			MqttProtocol.context.streamio = server.mqttmessages.MqttStream(reader, writer, **MqttProtocol.context.kwargs)
			MqttProtocol.context.state = MqttState.STATE_CONNECT
		except Exception as error:
			MqttProtocol.context.state = MqttState.STATE_CLOSE

	@staticmethod
	async def state_connect():
		""" Open mqtt state send connect """
		try:
			command = server.mqttmessages.MqttConnect(**MqttProtocol.context.kwargs)
			command.clean_session = True
			command.keep_alive = MqttProtocol.context.kwargs.get("keep_alive",120)
			await MqttProtocol.send(command)
			MqttProtocol.context.retry_count = 0
			MqttProtocol.context.state = MqttState.STATE_CONNACK
		except Exception as error:
			MqttProtocol.context.state = MqttState.STATE_CLOSE

	@staticmethod
	async def state_connack():
		""" Wait connection acknowledge state """
		await MqttStateMachine.state_receive()

	@staticmethod
	async def state_accepted():
		""" Connection mqtt accepted state """
		try:
			if len(MqttProtocol.subscriptions) > 0:
				command = server.mqttmessages.MqttSubscribe()
				for subscription in MqttProtocol.subscriptions.values():
					command.add_topic(subscription.topic, subscription.qos)
				await MqttProtocol.send(command)
			if len(MqttProtocol.publications) > 0:
				for publication in MqttProtocol.publications:
					await MqttProtocol.send(publication)
					publication.dup = 1
			MqttProtocol.context.state = MqttState.STATE_ESTABLISH
		except Exception as error:
			MqttProtocol.context.state = MqttState.STATE_CLOSE

	@staticmethod
	async def state_establish():
		""" Established mqtt state """
		await MqttStateMachine.state_receive()

	@staticmethod
	async def state_receive():
		""" Wait and treat message """
		try:
			# Read and decode message
			message = await server.mqttmessages.MqttMessage.receive(MqttProtocol.context.streamio)

			# If message decoded with success
			if message is not None:
				if MqttProtocol.context.debug:
					print("Mqtt receive : %s"%message.__class__.__name__)
				# Search treatment callback
				callback, kwargs = MqttProtocol.controls.get(message.control, [None,None])

				# If callback found
				if callback:
					# Call callback
					await callback(message, **kwargs)
				else:
					tools.logger.syslog("Mqtt callback not found for message=%d"%message.control)
			else:
				tools.logger.syslog("Mqtt lost connection")
				MqttProtocol.context.state = MqttState.STATE_CLOSE
		except Exception as error:
			MqttProtocol.context.state = MqttState.STATE_CLOSE

	@staticmethod
	async def state_close():
		""" Close mqtt state """
		try:
			if MqttProtocol.context.streamio is not None:
				await MqttProtocol.context.streamio.close()
				MqttProtocol.context.streamio = None
			MqttProtocol.context.state = MqttState.STATE_WAIT
		except Exception as error:
			MqttProtocol.context.state = MqttState.STATE_WAIT

	@staticmethod
	async def state_wait():
		""" Wait mqtt state before next reconnection """
		await uasyncio.sleep(10)
		display = False
		if   MqttProtocol.context.retry_count <= 60   and MqttProtocol.context.retry_count % 20 == 0:
			display = True
		elif MqttProtocol.context.retry_count <= 600  and MqttProtocol.context.retry_count % 60 == 0:
			display = True
		elif MqttProtocol.context.retry_count <= 3600 and MqttProtocol.context.retry_count % 3600 == 0:
			display = True
		if display:
			tools.logger.syslog("Mqtt not connected since %d s"%(MqttProtocol.context.retry_count))
		MqttProtocol.context.retry_count += 10
		MqttProtocol.context.state = MqttState.STATE_OPEN

	@staticmethod
	@MqttProtocol.add_control(server.mqttmessages.MQTT_CONNACK)
	async def on_conn_ack(message, **kwargs):
		""" Conn ack treatment """
		if MqttProtocol.context.state == MqttState.STATE_CONNACK:
			if message.return_code == 0:
				tools.logger.syslog("Mqtt connected")
				MqttProtocol.context.state = MqttState.STATE_ACCEPTED
			else:
				tools.logger.syslog("Mqtt connection refused %d"%message.return_code)
				MqttProtocol.context.state = MqttState.STATE_CLOSE
		else:
			tools.logger.syslog("Mqtt unexpected connack")
			MqttProtocol.context.state = MqttState.STATE_CLOSE

	@staticmethod
	@MqttProtocol.add_control(server.mqttmessages.MQTT_PINGREQ)
	async def on_ping_req(message, **kwargs):
		""" Ping received """
		if MqttProtocol.context.state == MqttState.STATE_ESTABLISH:
			await MqttProtocol.send(server.mqttmessages.MqttPingResp())
		else:
			tools.logger.syslog("Mqtt unexpected pingreq")
			MqttProtocol.context.state = MqttState.STATE_CLOSE

	@staticmethod
	@MqttProtocol.add_control(server.mqttmessages.MQTT_PINGRESP)
	async def on_ping_rsp(message, **kwargs):
		""" Ping response received """
		if MqttProtocol.context.state != MqttState.STATE_ESTABLISH:
			tools.logger.syslog("Mqtt unexpected pingres")
			MqttProtocol.context.state = MqttState.STATE_CLOSE

	@staticmethod
	@MqttProtocol.add_control(server.mqttmessages.MQTT_SUBACK)
	async def on_sub_ack(message, **kwargs):
		""" Subcribe acknowledge """
		if message.return_code[0] == server.mqttmessages.MQTT_SUBACK_FAILURE:
			tools.logger.syslog("Mqtt subscribe failed")

	@staticmethod
	@MqttProtocol.add_control(server.mqttmessages.MQTT_PUBACK)
	async def on_pub_ack(message, **kwargs):
		""" Publish ack received """
		for publication in MqttProtocol.publications:
			if publication.identifier == message.identifier:
				MqttProtocol.publications.remove(publication)
				break

	@staticmethod
	@MqttProtocol.add_control(server.mqttmessages.MQTT_PUBREC)
	async def on_pub_rec(message, **kwargs):
		""" Publish received """
		await MqttProtocol.send(server.mqttmessages.MqttPubRel(identifier=message.identifier))

	@staticmethod
	@MqttProtocol.add_control(server.mqttmessages.MQTT_PUBREL)
	async def on_pub_rel(message, **kwargs):
		""" Publish release received """
		await MqttProtocol.send(server.mqttmessages.MqttPubComp(identifier=message.identifier))

	@staticmethod
	@MqttProtocol.add_control(server.mqttmessages.MQTT_PUBCOMP)
	async def on_pub_comp(message, **kwargs):
		""" Publish complete received """
		MqttStateMachine.on_pub_ack(message, **kwargs)

	@staticmethod
	@MqttProtocol.add_control(server.mqttmessages.MQTT_UNSUBACK)
	async def on_unsub_ack(message, **kwargs):
		""" Unsubcribe acknowledge """

	@staticmethod
	@MqttProtocol.add_control(server.mqttmessages.MQTT_DISCONNECT)
	async def on_disconnect(message, **kwargs):
		""" Disconnect received """
		MqttProtocol.context.state = MqttState.STATE_CLOSE

	@staticmethod
	@MqttProtocol.add_control(server.mqttmessages.MQTT_PUBLISH)
	async def on_publish(message, **kwargs):
		""" Published message """
		if MqttProtocol.context.debug:
			print("Mqtt publish topic '%s', value='%s'"%(message.topic, message.value))
		await MqttProtocol.call_subscription(message)
		if message.qos == server.mqttmessages.MQTT_QOS_ONCE:
			pass
		elif message.qos == server.mqttmessages.MQTT_QOS_LEAST_ONCE:
			await MqttProtocol.send(server.mqttmessages.MqttPubAck(identifier=message.identifier))
		elif message.qos == server.mqttmessages.MQTT_QOS_EXACTLY_ONCE:
			await MqttProtocol.send(server.mqttmessages.MqttPubRec(identifier=message.identifier))

	@staticmethod
	async def task(**kwargs):
		""" Manages mqtt commands received and returns responses """
		try:
			states = {
				MqttState.STATE_OPEN      : ("OPEN",      MqttStateMachine.state_open),
				MqttState.STATE_CONNECT   : ("CONNECT",   MqttStateMachine.state_connect),
				MqttState.STATE_CONNACK   : ("CONNACK",   MqttStateMachine.state_connack),
				MqttState.STATE_ACCEPTED  : ("ACCEPTED",  MqttStateMachine.state_accepted),
				MqttState.STATE_ESTABLISH : ("ESTABLISH", MqttStateMachine.state_establish),
				MqttState.STATE_CLOSE     : ("CLOSE",     MqttStateMachine.state_close),
				MqttState.STATE_WAIT      : ("WAIT",      MqttStateMachine.state_wait)
			}
			previous_state_name = ""
			while True:
				state_name, callback = states.get(MqttProtocol.context.state, (None,None))
				if previous_state_name != state_name:
					if MqttProtocol.context.debug:
						print("Mqtt state   : %s"%state_name)
					previous_state_name = state_name
				if callback is not None:
					await callback()
				else:
					raise server.mqttmessages.MqttException("Mqtt illegal state")
		except Exception as err:
			tools.logger.syslog(err)
		finally:
			await MqttStateMachine.state_close()
