# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Presence simulator that plays sounds in the absence of the occupants of a dwelling """
def startup(**kwargs):
	""" Startup """
	import plugins.presencesimu.simulator
	plugins.presencesimu.simulator.PresenceSimu.start(**kwargs)
