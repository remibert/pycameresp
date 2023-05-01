# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Getch and vt100 utilities """
import sys
import tools.filesystem
import tools.strings

if tools.filesystem.ismicropython():
	from tools.keyboard_mcp import *
elif sys.platform == "win32":
	from tools.keyboard_win32 import *
else:
	from tools.keyboard_linux import *

screen_size = None
refresh_size = 0
def refresh_screen_size():
	""" Refresh the screen size """
	global screen_size
	try:
		sys.stdout.write("\x1B"+"7")      # Save cursor position
		sys.stdout.write("\x1B[999;999f") # Set cursor position far
		sys.stdout.write("\x1B[6n")       # Cursor position report
		try:
			sys.stdout.flush()
		except:
			pass

		size = getch(raw=False, duration=2, interchar=0.2)
		size = size[2:-1].split(";")
		screen_size = int(size[0]), int(size[1])
		if screen_size[0] < 5 or screen_size[1] < 5:
			result = screen_size
			screen_size = None
		else:
			result = screen_size
	except:
		screen_size = None
		result = (18,40)

	sys.stdout.write("\x1B"+"8") # Restore cursor position
	kbflush()
	return result

def get_screen_size(force=False):
	""" Get the VT100 screen size """
	# pylint:disable=global-variable-not-assigned
	global screen_size, refresh_size
	refresh_size += 1
	if refresh_size == 5:
		force = True
		refresh_size = 0
	if screen_size is not None and force is False:
		return screen_size
	else:
		return refresh_screen_size()
