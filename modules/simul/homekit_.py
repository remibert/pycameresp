# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Simulate homekit_ module """
class Accessory:
	""" Homekit accessory """
	def __init__(self, cid, name="Esp", manufacturer="Espressif", model="Esp32", serial_number="00112233445566", firmware_revision="1.0.0", hardware_revision="1.0.0", product_version="1.0"):
		""" Constructor """
	def __del__(self):
		""" Destructor """
	def deinit(self):
		""" Deinitialize """
	def add_server(self, server):
		""" Add server """
	def set_identify_callback(self, callback):
		""" Set identify callback """
	def set_product_data(self, data):
		""" Set product data """

class Server:
	""" Homkit server """
	def __init__(self, server_uuid):
		""" Constructor """
	def deinit(self):
		""" Deinitialize """
	def add_charact(self, charact):
		""" Add characteristic """

class Charact:
	""" Homekit characteristic """
	def __init__(self, uuid, typ, perm, value):
		""" Constructor """
	def deinit(self):
		""" Deinitialize """
	def set_unit(self, unit):
		""" Set unit """
	def set_description(self, description):
		""" Set description """
	def set_constraint(self, mini, maxi):
		""" Set min and max constraint """
	def set_step(self, step):
		""" Set step """
	def set_value(self, value):
		""" Set value """
	def get_value(self):
		""" Get value """
	def set_read_callback(self, callback):
		""" Set read callback """
	def set_write_callback(self, callback):
		""" Set write callback """
