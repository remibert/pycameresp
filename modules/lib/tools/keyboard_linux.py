# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Getch utilities for linux and osx """
import sys
import os
import select

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
	""" Read keyboard on os/x, linux """
	import tty
	import termios
	import fcntl
	fd = sys.stdin.fileno()
	oldattr = termios.tcgetattr(fd)
	oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
	try:
		newattr = oldattr[:]
		newattr[3] = newattr[3] & ~termios.ICANON
		newattr[3] = newattr[3] & ~termios.ECHO
		termios.tcsetattr(fd, termios.TCSANOW, newattr)

		fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

		if raw:
			tty.setraw(fd)
		result = b""
		try:
			inp, outp, err = select.select([sys.stdin], [], [], duration)
		except Exception as err:
			pass
		result = callback(inp)
	finally:
		# Reset the terminal:
		fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
		termios.tcsetattr(fd, termios.TCSAFLUSH, oldattr)
	return result

def kbflush(duration=0.5):
	""" Flush all keys not yet read """
