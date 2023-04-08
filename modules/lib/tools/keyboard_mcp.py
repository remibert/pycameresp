# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Getch utilities for micropython """
import sys
import select
import tools.filesystem
import tools.strings
import tools.watchdog

MAXINT = 100000000

# pylint:disable=ungrouped-imports
# pylint:disable=consider-using-enumerate
def getch(raw = True, duration=MAXINT, interchar=0.05):
	""" Wait a key pressed on keyboard and return it """
	key = b""
	tools.watchdog.WatchDog.feed()
	while 1:
		if len(key) == 0:
			delay = duration
		else:
			delay = interchar
		keyPressed = kbhit(delay)
		if tools.strings.is_key_ended(key):
			break
		if keyPressed:
			key += sys.stdin.buffer.read(1)
		else:
			if len(key) > 0:
				break
			elif delay < MAXINT:
				break

	try:
		key = key.decode("utf8")
	except:
		key = tools.strings.dump(key,withColor=False)
	return key

def kbhit(duration=0.01):
	""" Indicates if a key is pressed or not """
	r,w,e = select.select([sys.stdin],[],[],duration)
	if r != []:
		return True
	return False

def kbflush(duration=0.1):
	""" Flush all keys not yet read """
	while 1:
		r,w,e = select.select([sys.stdin],[],[],duration)
		if r != []:
			sys.stdin.buffer.read(1)
		else:
			break
