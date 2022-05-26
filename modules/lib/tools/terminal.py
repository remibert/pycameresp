# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Getch and vt100 utilities """
import sys
import os
import select
try:
	from tools import filesystem, strings,watchdog
except:
	# pylint:disable=multiple-imports
	import strings,filesystem
	if filesystem.ismicropython():
		import watchdog


MAXINT = 100000000

if filesystem.ismicropython():
	# pylint:disable=ungrouped-imports
	# pylint:disable=consider-using-enumerate
	def getch(raw = True, duration=MAXINT, interchar=0.05):
		""" Wait a key pressed on keyboard and return it """
		key = b""
		watchdog.WatchDog.feed()
		while 1:
			if len(key) == 0:
				delay = duration
			else:
				delay = interchar
			keyPressed = kbhit(delay)
			if strings.is_key_ended(key):
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
			key = strings.dump(key,withColor=False)
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
else:
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

		size = getch(raw=False, duration=1, interchar=0.2)
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
	global screen_size, refresh_size
	refresh_size += 1
	if refresh_size == 5:
		force = True
		refresh_size = 0
	if screen_size is not None and force is False:
		return screen_size
	else:
		return refresh_screen_size()
