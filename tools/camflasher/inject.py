import sys
sys.path.append("../../modules/lib/tools")
import filesystem
import strings
import os.path
import binascii

class PythonPrompt:
	def __init__(self, device):
		self.data = b""
		self.device = device

	def read_byte(self, byte):
		self.data += byte
		# print(self.data)
		if self.data[-3:] == b"=> ":
			raise Exception("Shell not exiting")
		if self.data[-4:] == b">>> ":
			return self.data
		elif self.data[-6:] == b"\r\n... ":
			self.device.write(b"\x0D")
		return None

	def cmd(self, command="", timeout=None, max_count=256):
		if timeout is not None:
			self.device.timeout = timeout
		self.data = b""
		self.device.write(b"%s\x0D"%strings.tobytes(command))
		
		for i in range(max_count):
			data = self.device.read(1)
			if data != b"":
				if self.read_byte(data) is not None:
					break
		result = self.epurate()
		print('>>> %s'%command)
		if result is not None:
			print(result)
		print(self.data)
		return result
		
	def epurate(self):
		lines = strings.tostrings(self.data).split("\n")[1:-1]
		result = []
		
		for line in lines:
			try:
				result.append(eval(line.strip()))
			except:
				result.append(Exception(line.strip()))
		if len(result) == 0:
			return None
		else:
			return result[-1]
		
	def makedir(self, directory):
		""" Make directory recursively """
		import os.path
		result = True
		directories = [directory]
		while 1:
			parts = os.path.split(directory)
			if parts[1] == "" or parts[0] == "":
				break
			directories.append(parts[0])
			directory = parts[0]

		self.cmd("import os")
		directories.reverse()
		for d in directories:
			if d != "/":
				res = self.cmd("os.stat('%s')"%d)
				if type(res) != type((0,)):
					res = self.cmd("os.mkdir('%s')"%d)
					if res is not None:
						result = False
						break
		return result

	def exit_shell(self):
		self.cmd("exit")

	def set_date(self, date = None):
		result = True
		if self.cmd("import machine") is None:
			year,month,day,hour,minute,second = strings.local_time(date)[:6]
			if self.cmd("machine.RTC().datetime((%d,%d,%d,%d,%d,%d,%d,%d))"%(year, month, day, 0, hour, minute, second, 0)) is not None:
				result = False
		return result
	
	def copy_file(self, root, filename):
		result = False
		with open(filename, "rb") as in_file:
			result = True
			target_filename = filename[len(root):]
			directory, _ = os.path.split(target_filename)
			if self.makedir(directory):
				print("+",target_filename, end="")
				self.cmd("import binascii")
				self.cmd("import machine")
				current_date = None
				if self.cmd("f=open('%s','wb')"%target_filename) is None:
					file_date = strings.local_time(filesystem.filetime(filename))

					self.cmd('def w(f,d,s): return f.write(binascii.a2b_base64(d)) == s')
					chunk = bytearray(160)
					size = filesystem.filesize(filename)
					while size > 0:
						length = in_file.readinto(chunk)
						size -= length
						part = binascii.b2a_base64(chunk[:length])
						if size <= len(chunk):
							current_date = self.cmd("machine.RTC().datetime()")
							year,month,day,hour,minute,second = file_date[:6]
							if self.cmd("machine.RTC().datetime((%d,%d,%d,%d,%d,%d,%d,%d))"%(year, month, day, 0, hour, minute, second, 0)) is not None:
								result = False
								break
						if self.cmd('w(f,%s,%d)'%(part, length)) is False:
							result = False
							break
					self.cmd("f.close()")
					if current_date is not None:
						self.cmd("machine.RTC().datetime(%s)"%repr(current_date))
				if result:
					print(" Ok")
				else:
					print(" FAILED")
			else:
				print("! Cannot create directory '%s'"%directory)
		return result


def inject(root, paths):
	import serial
	from serial.tools import list_ports

	ports = []
	for port, a, b in sorted(list_ports.comports()):
		if not "Bluetooth" in port and not "Wireless" in port and "cu.BLTH" not in port and port != "COM1":
			ports.append(port)
	device = serial.Serial(port=ports[0], baudrate=115200, timeout=1)

	while len(device.read(1)) >= 1:
		pass
	device.reset_input_buffer()
	prompt = PythonPrompt(device)

	# prompt.cmd("\x03")
	# prompt.exit_shell()

	# prompt.cmd("import time")
	# r = prompt.cmd("time.sleep (1000)", timeout=0.1)
	for path in paths:
		_, filenames = filesystem.scandir(root + "/" + path,"*.mpy",True)
		for filename in filenames:
			prompt.copy_file(root, filename)

	prompt.set_date()
	device.close()

if __name__ == "__main__":
	#~ root = "/Users/remi/Downloads/firmware/micropython/ports/esp32/build-ESP32CAM/frozen_mpy"
	#~ inject(root, ["shell","tools"])
	root = "/Users/remi/Downloads/firmware/lib 2"
	inject(root, ["shell","tools"])
