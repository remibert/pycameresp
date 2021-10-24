# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Outlet homekit accessory """
from homekit import *

class Outlet(Accessory):
	""" Outlet homekit accessory """
	def __init__(self, **kwargs):
		""" Create outlet accessory. Parameters : name(string), on(bool), outlet_in_use(bool) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_OUTLET, **kwargs)
		self.server = Server(name=kwargs.get("name","Outlet"), server_uuid=Server.UUID_OUTLET)

		self.on = charact_bool_create (Charact.UUID_ON, Charact.PERM_RWE, kwargs.get("on",False))
		self.server.add_charact(self.on)

		self.outlet_in_use = charact_bool_create (Charact.UUID_OUTLET_IN_USE, Charact.PERM_RE, kwargs.get("outlet_in_use",False))
		self.server.add_charact(self.outlet_in_use)

		self.on.set_write_callback(self.write_on)
		self.add_server(self.server)

	def write_on(self, charact):
		""" Write on """
		if charact.get_value():
			print("ON")
		else:
			print("OFF")

def main():
	""" Test """
	# Initialize homekit engine
	Homekit.init()

	# Create accessory
	Homekit.play(Outlet(name="My Outlet"))

if __name__ == "__main__":
	main()
