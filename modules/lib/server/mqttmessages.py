# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
# pylint:disable=consider-using-f-string
""" Mqtt messages classes """
import io
import wifi.hostname
import server.stream
import tools.strings

MQTT_UNDEFINED   = 0
MQTT_CONNECT     = 1  # Client to Server                     : Client request to connect to Server
MQTT_CONNACK     = 2  # Server to Client                     : Connect acknowledgment
MQTT_PUBLISH     = 3  # Client to Server or Server to Client : Publish message
MQTT_PUBACK      = 4  # Client to Server or Server to Client : Publish acknowledgment
MQTT_PUBREC      = 5  # Client to Server or Server to Client : Publish received (assured delivery part 1)
MQTT_PUBREL      = 6  # Client to Server or Server to Client : Publish release (assured delivery part 2)
MQTT_PUBCOMP     = 7  # Client to Server or Server to Client : Publish complete (assured delivery part 3)
MQTT_SUBSCRIBE   = 8  # Client to Server                     : Client subscribe request
MQTT_SUBACK      = 9  # Server to Client                     : Subscribe acknowledgment
MQTT_UNSUBSCRIBE = 10 # Client to Server                     : Unsubscribe request
MQTT_UNSUBACK    = 11 # Server to Client                     : Unsubscribe acknowledgment
MQTT_PINGREQ     = 12 # Client to Server                     : PING request
MQTT_PINGRESP    = 13 # Server to Client                     : PING response
MQTT_DISCONNECT  = 14 # Client to Server                     : Client is disconnecting

MQTT_QOS_ONCE         = 0 # At most once delivery
MQTT_QOS_LEAST_ONCE   = 1 # At least once delivery
MQTT_QOS_EXACTLY_ONCE = 2 # Exactly once delivery

MQTT_CONNACK_ACCEPTED              = 0 # Connection Accepted
MQTT_CONNACK_UNACCEPTABLE_PROTOCOL = 1 # Connection refused : The Server does not support the level of the MQTT protocol requested by the Client
MQTT_CONNACK_IDENTIFIER_REJECTED   = 2 # Connection refused : The Client identifier is correct UTF-8 but not allowed by the Server
MQTT_CONNACK_SERVER_UNAVAILABLE    = 3 # Connection refused : The Network Connection has been made but the MQTT service is unavailable
MQTT_CONNACK_BAD_USER              = 4 # Connection refused : Bad user name or password, the data in the user name or password is malformed
MQTT_CONNACK_NOT_AUTHORIZED        = 5 # Connection refused : The Client is not authorized to connect

MQTT_SUBACK_MAX_QOS0 = 0x00 # Success - Maximum QoS 0
MQTT_SUBACK_MAX_QOS1 = 0x01 # Success - Maximum QoS 1
MQTT_SUBACK_MAX_QOS2 = 0x02 # Success - Maximum QoS 2
MQTT_SUBACK_FAILURE  = 0x80 # Failure

class MqttException(Exception):
	""" Exception for MQTT layer """
	def __init__(self, message):
		""" Exception constructor """
		Exception.__init__(self)
		self.message = message

class MqttMessage:
	""" Selection class of commands received """
	messages = {}
	identifier_base = [1]
	def __init__(self, **kwargs):
		""" Constructor 
		Parameters :
			control    : type of message (MQTT_CONNECT,MQTT_CONNACK,MQTT_PUBLISH,MQTT_PUBACK,MQTT_PUBREC,MQTT_PUBREL,MQTT_PUBCOMP,MQTT_SUBSCRIBE,MQTT_SUBACK,MQTT_UNSUBSCRIBE,MQTT_UNSUBACK,MQTT_PINGREQ,MQTT_PINGRESP,MQTT_DISCONNECT)
			qos        : quality of service (MQTT_QOS_ONCE,MQTT_QOS_LEAST_ONCE,MQTT_QOS_EXACTLY_ONCE)
			retain     : retain message (0 or 1)
			dup        : duplicate delivery control payload (0 or 1)
			identifier : packet identifier (1 to 65535)"""
		if kwargs.get("header",None) is None:
			self.control    = kwargs.get("control"   ,MQTT_UNDEFINED)
			self.qos        = kwargs.get("qos"       ,MQTT_QOS_ONCE)
			self.dup        = kwargs.get("dup"       ,0)
			self.retain     = kwargs.get("retain"    ,0)
			self.identifier = kwargs.get("identifier",None)
			if self.identifier is None:
				self.identifier = MqttMessage.identifier_base[0]
				MqttMessage.identifier_base[0] += 1
			self.header = None
		else:
			self.decode_header(kwargs.get("header"))
		self.payload = io.BytesIO()
		self.buffer = io.BytesIO()

	@staticmethod
	def init():
		""" Initialize the message selector """
		if len(MqttMessage.messages) == 0:
			MqttMessage.messages = {\
				MQTT_CONNECT     : MqttConnect,
				MQTT_CONNACK     : MqttConnAck,
				MQTT_PUBLISH     : MqttPublish,
				MQTT_PUBACK      : MqttPubAck,
				MQTT_PUBREC      : MqttPubRec,
				MQTT_PUBREL      : MqttPubRel,
				MQTT_PUBCOMP     : MqttPubComp,
				MQTT_SUBSCRIBE   : MqttSubscribe,
				MQTT_SUBACK      : MqttSubAck,
				MQTT_UNSUBSCRIBE : MqttUnsubscribe,
				MQTT_UNSUBACK    : MqttUnSubAck,
				MQTT_PINGREQ     : MqttPingReq,
				MQTT_PINGRESP    : MqttPingResp,
				MQTT_DISCONNECT  : MqttDisconnect,}

	@staticmethod
	async def receive(streamio):
		""" Wait message and return the message decoded """
		MqttMessage.init()
		header = await streamio.read(1)
		if len(header) > 0:
			control = header[0] >> 4
			# If message is recognized
			if control in MqttMessage.messages:
				# Create the right message
				result = MqttMessage.messages[control](header=header)
				await result.read(streamio)
				return result
		return None

	def decode_header(self, data):
		""" Decode header """
		self.header = data
		self.control = (data[0] >> 4)
		self.qos     = (data[0] >> 1) & 3
		self.dup     = (data[0] >> 3) & 1
		self.retain  = (data[0] & 1)

	def encode_header(self):
		""" Encode header """
		if self.control in [MQTT_CONNECT , MQTT_CONNACK, MQTT_PUBACK,
			MQTT_PUBREC , MQTT_PUBCOMP , MQTT_SUBACK,  MQTT_UNSUBACK,
			MQTT_PINGREQ, MQTT_PINGRESP, MQTT_DISCONNECT]:
			return (self.control << 4).to_bytes(1, "big")
		elif self.control in [MQTT_SUBSCRIBE, MQTT_UNSUBSCRIBE, MQTT_PUBREL]:
			return ((self.control << 4) | 2).to_bytes(1, "big")
		elif self.control in [MQTT_PUBLISH]:
			return ((self.control  << 4) | ((self.dup & 1) << 3) | ((self.qos & 3) << 1) | ((self.retain & 1))).to_bytes(1, "big")
		else:
			raise MqttException("Mqtt control command not supported")


	def encode_length(self, length):
		""" Encode the length """
		result = b""
		x = length
		while True:
			encoded_byte = x % 128
			x = x >> 7
			if x > 0:
				encoded_byte |= 0x80
			result += encoded_byte.to_bytes(1, "big")
			if x <= 0:
				break
		return result


	async def write_length(self, streamio):
		""" Write the length of message """

		length = len(self.payload.getvalue())
		x = length
		while True:
			encoded_byte = x % 128
			x = x >> 7
			if x > 0:
				encoded_byte |= 0x80
			await streamio.write(encoded_byte.to_bytes(1, "big"))
			if x <= 0:
				break
		return length

	async def read_length(self, streamio):
		""" Read the length """
		multiplier = 1
		length = 0
		while True:
			encoded_byte = await streamio.read(1)
			length += (encoded_byte[0] & 0x7F) * multiplier
			multiplier *= 128
			if multiplier > 128*128*128:
				raise MqttException("Mqtt malformed remaining length")
			if encoded_byte[0] & 0x80 == 0:
				break
		return length

	async def write(self, streamio):
		""" Write message """
		self.buffer.write(self.encode_header())
		self.encode()
		self.buffer.write(self.encode_length(len(self.payload.getvalue())))
		if await streamio.write(self.buffer.getvalue()) > 0:
			await streamio.write(self.payload.getvalue())

	async def read(self, streamio):
		""" Read message """
		if self.header is None:
			self.decode_header(await streamio.read(1))
		length = await self.read_length(streamio)
		if length > 0:
			self.payload = io.BytesIO(await streamio.read(length))
		self.decode()

	def put_string(self, data):
		""" Put the string with its length """
		if data is not None:
			if type(data) == type(0):
				data = "%d"%data
			self.put_int(len(data))
			self.payload.write(tools.strings.tobytes(data))

	def put_int(self, value):
		""" Put integer on 2 bytes """
		self.payload.write(value.to_bytes(2, "big"))

	def put_byte(self, value):
		""" Put byte integer """
		self.payload.write(value.to_bytes(1, "big"))

	def put_buffer(self, value):
		""" Put binary buffer """
		self.payload.write(tools.strings.tobytes(value))

	def get_string(self):
		""" Get the string with its length """
		return tools.strings.tostrings(self.payload.read(self.get_int()))

	def get_int(self):
		""" Get integer on 2 bytes """
		return int.from_bytes(self.payload.read(2), "big")

	def get_byte(self):
		""" Put byte integer """
		return int.from_bytes(self.payload.read(1), "big")

	def decode(self):
		""" Decode message (must redefined)"""

	def encode(self):
		""" Encode message (must redefined)"""

class MqttConnect(MqttMessage):
	""" Client to Server : Client request to connect to Server """
	def __init__(self, **kwargs):
		""" Constructor 
		Parameters :
			username      : user name (string)
			password      : password (string)
			will_retain   : this bit specifies if the Will Message is to be Retained when it is published (0 or 1)
			will_qos      : These two bits specify the QoS level to be used when publishing the Will Message (0 or 1)
			will_flag     : will flag see mqtt specification (0 or 1)
			clean_session : this bit specifies the handling of the Session state (0 or 1)
			keep_alive    : the keep alive is a time interval measured in seconds (int)
			client_id     : the client identifier identifies the client to the server (string)
		"""
		MqttMessage.__init__(self, control=MQTT_CONNECT, **kwargs)
		self.protocol_name  = "MQTT"
		self.protocol_level = 4 # MQTT 3.1.1
		self.username       = kwargs.get("username",     None)
		self.password       = kwargs.get("password",     None)
		self.will_retain    = kwargs.get("will_retain",  False)
		self.will_qos       = kwargs.get("qos",          MQTT_QOS_ONCE)
		self.will_flag      = kwargs.get("will_flag",    False)
		self.clean_session  = kwargs.get("clean_session",False)
		self.keep_alive     = kwargs.get("keep_alive",   60)
		self.client_id      = kwargs.get("client_id",    wifi.hostname.Hostname().get_hostname())

	def encode(self):
		""" Encode the full message """
		self.put_string (self.protocol_name)
		self.put_byte   (self.protocol_level)
		self.put_byte   (self.get_flags())
		self.put_int    (self.keep_alive)
		self.put_string (self.client_id)
		self.put_string (self.username)
		self.put_string (self.password)

	def get_flags(self):
		""" Encode flags """
		# pylint:disable=multiple-statements
		result = 0
		if self.username is not None:      result |= 0x80
		if self.password is not None:      result |= 0x40
		if self.will_retain:   result |= 0x20
		if self.will_qos:      result |= ((self.will_qos << 3) & 0x18)
		if self.will_flag:     result |= 4
		if self.clean_session: result |= 2
		return result

	def decode(self):
		""" Read content """
		self.protocol_name  = self.get_string()
		self.protocol_level = self.get_byte()
		flags = self.get_byte()
		self.will_flag     = (flags & 0x04) >> 2
		self.will_qos      = (flags & 0x18) >> 3
		self.will_retain   = (flags & 0x20) >> 5
		self.clean_session = (flags & 0x01)
		self.keep_alive    = self.get_int()
		self.client_id     = self.get_string()
		if flags & 0x80:
			self.username  = self.get_string()
		if flags & 0x40:
			self.password  = self.get_string()

class MqttConnAck(MqttMessage):
	""" Server to Client : Connect acknowledgment """
	def __init__(self, **kwargs):
		""" Constructor 
		Parameters :
			return_code : return code (MQTT_CONNACK_ACCEPTED,MQTT_CONNACK_UNACCEPTABLE_PROTOCOL,MQTT_CONNACK_IDENTIFIER_REJECTED,MQTT_CONNACK_SERVER_UNAVAILABLE,MQTT_CONNACK_BAD_USER,MQTT_CONNACK_NOT_AUTHORIZED)
			session_present_flag :  session present flag (0 or 1)
		"""
		MqttMessage.__init__(self, control=MQTT_CONNACK, **kwargs)
		self.return_code          = kwargs.get("return_code",MQTT_CONNACK_ACCEPTED)
		self.session_present_flag = kwargs.get("session_present_flag",0)

	def decode(self):
		""" Decode payload """
		self.session_present_flag = self.get_byte() & 0x01
		self.return_code          = self.get_byte()

	def encode(self):
		""" Encode payload """
		self.put_byte(self.session_present_flag & 0x01)
		self.put_byte(self.return_code)

class MqttPingReq(MqttMessage):
	""" Client to Server : PING request """
	def __init__(self, **kwargs):
		""" Constructor """
		MqttMessage.__init__(self, control=MQTT_PINGREQ, **kwargs)

class MqttPingResp(MqttMessage):
	""" Server to Client : PING response """
	def __init__(self, **kwargs):
		""" Constructor """
		MqttMessage.__init__(self, control=MQTT_PINGRESP, **kwargs)

class MqttPublish(MqttMessage):
	"""Client to Server or Server to Client : Publish message """
	def __init__(self, **kwargs):
		""" Constructor 
		Parameters : 
			topic : topic name
			value : topic value """
		MqttMessage.__init__(self, control=MQTT_PUBLISH, **kwargs)
		self.topic = kwargs.get("topic","")
		self.value = kwargs.get("value","")
		self.identifier = 0

	def decode(self):
		""" Decode payload """
		self.topic      = self.get_string()
		if self.qos in [MQTT_QOS_LEAST_ONCE, MQTT_QOS_EXACTLY_ONCE]:
			self.identifier = self.get_int()
		self.value    = self.payload.read()

	def encode(self):
		""" Encode the payload """
		self.put_string(self.topic)
		if self.qos in [MQTT_QOS_LEAST_ONCE, MQTT_QOS_EXACTLY_ONCE]:
			self.put_int(self.identifier)
		self.put_buffer(self.value)

class MqttPubAck(MqttMessage):
	""" Client to Server or Server to Client : Publish acknowledgment """
	def __init__(self, **kwargs):
		""" Constructor """
		MqttMessage.__init__(self, control=MQTT_PUBACK, **kwargs)

	def decode(self):
		""" Decode payload """
		self.identifier = self.get_int()

	def encode(self):
		""" Encode the payload """
		self.put_int(self.identifier)

class MqttPubRec(MqttMessage):
	""" Client to Server or Server to Client : Publish received (assured delivery part 1) """
	def __init__(self, **kwargs):
		""" Constructor """
		MqttMessage.__init__(self, control=MQTT_PUBREC, **kwargs)

	def decode(self):
		""" Decode payload """
		self.identifier = self.get_int()

	def encode(self):
		""" Encode the payload """
		self.put_int(self.identifier)

class MqttPubRel(MqttMessage):
	""" Client to Server or Server to Client : Publish release (assured delivery part 2) """
	def __init__(self, **kwargs):
		""" Constructor """
		MqttMessage.__init__(self, control=MQTT_PUBREL, **kwargs)

	def decode(self):
		""" Decode payload """
		self.identifier = self.get_int()

	def encode(self):
		""" Encode the payload """
		self.put_int(self.identifier)

class MqttPubComp(MqttMessage):
	""" Client to Server or Server to Client : Publish complete (assured delivery part 3) """
	def __init__(self, **kwargs):
		""" Constructor """
		MqttMessage.__init__(self, control=MQTT_PUBCOMP, **kwargs)

	def decode(self):
		""" Decode payload """
		self.identifier = self.get_int()

	def encode(self):
		""" Encode the payload """
		self.put_int(self.identifier)

class MqttSubscribe(MqttMessage):
	""" Client to Server : Client subscribe request """
	def __init__(self, **kwargs):
		""" Constructor """
		MqttMessage.__init__(self, control=MQTT_SUBSCRIBE, **kwargs)
		self.topics = kwargs.get("topics",[])

	def add_topic(self, topic, qos=MQTT_QOS_ONCE):
		""" Add topics into subscribe """
		self.topics.append((topic, qos))

	def decode(self):
		""" Decode payload """
		self.identifier = self.get_int()
		self.topics = []
		while self.payload.tell() < len(self.payload.getvalue()):
			topic = self.get_string()
			qos = self.get_byte()
			self.add_topic(topic, qos)

	def encode(self):
		""" Encode payload """
		self.put_int(self.identifier)
		for topic,qos in self.topics:
			self.put_string(topic)
			self.put_byte(qos)

class MqttSubAck(MqttMessage):
	""" Server to Client : Subscribe acknowledgment """
	def __init__(self, **kwargs):
		""" Constructor """
		MqttMessage.__init__(self, control=MQTT_SUBACK, **kwargs)
		self.return_code = kwargs.get("return_code",[])

	def decode(self):
		""" Decode payload """
		self.identifier = self.get_int()
		self.return_code = []
		while self.payload.tell() < len(self.payload.getvalue()):
			self.return_code.append(self.get_byte())

	def encode(self):
		""" Encode payload """
		self.put_int(self.identifier)
		for return_code in self.return_code:
			self.put_byte(return_code)

class MqttUnsubscribe(MqttMessage):
	""" Client to Server : Unsubscribe request """
	def __init__(self, **kwargs):
		""" Constructor """
		MqttMessage.__init__(self, control=MQTT_UNSUBSCRIBE, **kwargs)
		self.topics = kwargs.get("topics",[])

	def add_topic(self, topic):
		""" Add topics into subscribe """
		self.topics.append(topic)

	def decode(self):
		""" Decode payload """
		self.identifier = self.get_int()
		self.topics = []
		while self.payload.tell() < len(self.payload.getvalue()):
			topic = self.get_string()
			self.add_topic(topic)

	def encode(self):
		""" Encode payload """
		self.put_int(self.identifier)
		for topic,qos in self.topics:
			self.put_string(topic)

class MqttUnSubAck(MqttMessage):
	""" Server to Client : Unsubscribe acknowledgment """
	def __init__(self, **kwargs):
		""" Constructor """
		MqttMessage.__init__(self, control=MQTT_UNSUBACK, **kwargs)

	def decode(self):
		""" Decode payload """
		self.identifier = self.get_int()

	def encode(self):
		""" Encode the payload """
		self.put_int(self.identifier)

class MqttDisconnect(MqttMessage):
	""" Client to Server : Client is disconnecting """
	def __init__(self, **kwargs):
		""" Constructor """
		MqttMessage.__init__(self, control=MQTT_DISCONNECT, **kwargs)

class MqttStream(server.stream.Stream):
	""" Read and write stream for mqtt """
	def __init__(self, reader, writer, **kwargs):
		""" Constructor """
		server.stream.Stream.__init__(self, reader, writer)
		self.dump_activated = kwargs.get("dump",False)

	async def read(self, length):
		""" Read data from the stream """
		result = await server.stream.Stream.read(self, length)
		if self.dump_activated:
			if len(result) > 0:
				print("  Read :")
				self.dump(result)
		return result

	async def write(self, data):
		""" Write data in the stream """
		if self.dump_activated:
			if len(data) > 0:
				print("  Write :")
				self.dump(data)
		return await server.stream.Stream.write(self, data)

	def dump(self, data):
		""" Dump data """
		width = 16
		offset = 0
		file = io.BytesIO()
		while True:
			line = io.BytesIO()
			line.write(b'    %08X  ' % offset)
			tools.strings.dump_line(data[offset:offset+width], line, width)
			offset += width
			print(tools.strings.tostrings(line.getvalue()))
			if offset >= len(data):
				break
