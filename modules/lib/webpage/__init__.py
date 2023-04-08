# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" All web pages defined here """
import webpage.passwordpage
import webpage.mainpage
import webpage.changepasswordpage
import webpage.infopage
import webpage.pushoverpage
import webpage.serverpage
import webpage.wifipage
import webpage.regionpage
import webpage.presencepage
import webpage.awakepage
import webpage.systempage
import webpage.webhookpage
import webpage.mqttpage
import tools.info
import tools.support

if tools.support.battery():
	# pylint:disable=ungrouped-imports
	import webpage.batterypage

if tools.info.iscamera():
	# pylint:disable=ungrouped-imports
	import webpage.streamingpage
	import webpage.camerapage
	import webpage.historicpage
	import webpage.motionpage
