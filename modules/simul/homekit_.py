class Accessory:
	def __init__(self, cid, name="Esp", manufacturer="Espressif", model="Esp32", serialNumber="00112233445566", firmwareRevision="1.0.0", hardwareRevision="1.0.0", productVersion="1.0"): pass
	def __del__(self): pass
	def deinit(self):pass
	def addServer(self, server): pass
	def setIdentifyCallback(self, callback): pass
	def setProductData(self, data): pass

class Server:
	def __init__(self, serverUuid): pass
	def deinit(self): pass
	def addCharact(self, charact): pass

class Charact:
	def __init__(self, uuid, typ, perm, value): pass
	def deinit(self): pass
	def setUnit(self, unit): pass
	def setDescription(self, description): pass
	def setConstraint(self, mini, maxi): pass
	def setStep(self, step): pass
	def setValue(self, value): pass
	def getValue(self): pass
	def setReadCallback(self, callback): pass
	def setWriteCallback(self, callback): pass
