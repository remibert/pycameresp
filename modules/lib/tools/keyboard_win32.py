# Distributed under Pycameresp License
# Copyright (c) 2023 Remi BERTHOLET
""" Getch utilities for windows """

MAXINT = 100000000

def getch(raw = True, duration=MAXINT, interchar=0.01):
	""" Wait a key pressed on keyboard and return it """
	return read_keyboard(duration, raw, get_char)

def kbhit(duration=0.001):
	""" Indicates if a key is pressed or not """
	return read_keyboard(duration, True, test_char)

def get_char(stdins):
	""" Get character """
	if stdins != []:
		return stdins[0].read()
	return b""

def test_char(stdins):
	""" Test a character """
	if stdins != []:
		return True
	return False

def read_keyboard(duration=0.001, raw=True, callback=None):
	""" Read keyboard on os/x, linux or windows"""
	# pylint:disable=import-error
	# pylint:disable=unreachable
	import msvcrt
	import time
	start = time.process_time()
	end = start + duration
	result = b""
	while True:
		break
		if msvcrt.kbhit():
			result = msvcrt.getch()
			break
		current = time.process_time()
		if time.process_time() > end:
			break
		else:
			time.sleep(duration/100)
	return result

def kbflush(duration=0.5):
	""" Flush all keys not yet read """
