# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" All web pages defined here """
from webpage.passwordpage       import *
from webpage.mainpage           import *
from webpage.changepasswordpage import *
from webpage.infopage           import *
from webpage.pushoverpage       import *
from webpage.serverpage         import *
from webpage.wifipage           import *
from webpage.regionpage         import *
from webpage.presencepage       import *
from webpage.batterypage        import *
from webpage.awakepage          import *
from webpage.systempage         import *
from tools.useful               import iscamera
if iscamera():
	# pylint:disable=ungrouped-imports
	from webpage.streamingpage  import *
	from webpage.camerapage     import *
	from webpage.historicpage   import *
	from webpage.motionpage     import *
