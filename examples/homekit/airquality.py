# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Air quality homekit accessory """
from homekit import *

class AirQualitySensor(Accessory):
	""" Air quality homekit accessory """
	def __init__(self, **kwargs):
		""" Create air quality accessory. Parameters : name(string), air_quality(int) and all Accessory parameters """
		Accessory.__init__(self, Accessory.CID_SENSOR, **kwargs)

		self.server = Server(name=kwargs.get("name","Air quality sensor"), server_uuid=Server.UUID_AIR_QUALITY_SENSOR)

		self.air_quality = charact_uint8_create (Charact.UUID_AIR_QUALITY, Charact.PERM_RE, kwargs.get("air_quality",0))
		self.air_quality.set_constraint(0, 5, 1)
		self.server.add_charact(self.air_quality)

		self.add_server(self.server)

	def set_air_quality(self, value):
		""" Set the air quality """
		self.air_quality.set_value(value)

def main():
	""" Test """
	# Initialize homekit engine
	Homekit.init()

	# Create air quality sensor
	sensor = AirQualitySensor(name="My air quality sensor", air_quality=0)

	# Create accessory
	Homekit.play(sensor)

	import time
	air_quality = 0

	# Manage the air quality (simple sample)
	while True:
		time.sleep(2)

		air_quality += 1
		if air_quality > 5:
			air_quality = 0

		# Change the accessory air quality
		sensor.set_air_quality(air_quality)

if __name__ == "__main__":
	main()
