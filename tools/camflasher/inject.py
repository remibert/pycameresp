""" Inject files read from github into device, using python prompt """
import sys
import os.path
import binascii
import io
import zipfile
from re import split
import requests
import serial
from serial.tools import list_ports
sys.path.append("../../modules/lib/tools")
# pylint:disable=import-error
# pylint:disable=wrong-import-position
import filesystem
import strings

GITHUB_HOST = 'https://github.com'
PYCAMERESP_PATH = 'remibert/pycameresp/releases'

class BinaryReader:
	""" Binary file reader with filename """
	def __init__(self, filename):
		""" Constructor """
		self.file = open(filename, "rb")
		self.filename = filename

	def __del__(self):
		""" Close file """
		self.file.close()

	def readinto(self, byte_array):
		""" Read into the byte array """
		return self.file.readinto(byte_array)

	def get_size(self):
		""" Return the size of file """
		return filesystem.filesize(self.filename)

	def get_date_time(self):
		""" Return the tuple with date and time of file """
		return strings.local_time(filesystem.filetime(self.filename))[:6]

class ZipReader:
	""" Zip binary file reader """
	def __init__(self, byte_array, date_time):
		""" Constructor """
		self.file = io.BytesIO(byte_array)
		self.size = len(byte_array)
		self.date_time = date_time

	def readinto(self, byte_array):
		""" Read into the byte array """
		return self.file.readinto(byte_array)

	def get_size(self):
		""" Return the size of file """
		return self.size

	def get_date_time(self):
		""" Return the tuple with date and time of file """
		return self.date_time

class PythonPrompt:
	""" Class to send command to python prompt """
	def __init__(self, device, printer=None, verbose=False):
		self.data = b""
		self.device = device
		self.verbose = verbose
		self.printer  = printer

	def read_byte(self, byte):
		""" Read byte and analyse response """
		self.data += byte
		# self.print(self.data)
		if self.data[-3:] == b"=> ":
			raise Exception("Shell already existing")
		if self.data[-4:] == b">>> ":
			return self.data
		elif self.data[-6:] == b"\r\n... ":
			self.device.write(b"\x0D")
		return None

	def command(self, cmd="", timeout=None, max_count=256):
		""" Send command line to python prompt and return result get """
		if timeout is not None:
			self.device.timeout = timeout
		self.data = b""
		self.device.write(b"%s\x0D"%strings.tobytes(cmd))

		line = b""
		for _ in range(max_count):
			data = self.device.read(1)
			if data != b"":
				line += data
				if self.read_byte(data) is not None:
					break
		result = self.epurate()
		if self.verbose:
			self.print('>>> %s'%cmd)
		if result is not None:
			if self.verbose:
				self.print(result)
		if self.verbose:
			self.print(self.data)
		return result

	def print(self, message, end="\n"):
		""" Print message """
		if self.printer is None:
			print(message, end=end)
		else:
			self.printer(message, end)

	def epurate(self):
		""" Epurate python response """
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
		result = True
		directories = [directory]
		while 1:
			parts = os.path.split(directory)
			if parts[1] == "" or parts[0] == "":
				break
			directories.append(parts[0])
			directory = parts[0]

		self.command("import os")
		directories.reverse()
		for d in directories:
			if d != "/":
				res = self.command("os.stat('%s')"%d)
				if type(res) != type((0,)):
					res = self.command("os.mkdir('%s')"%d)
					if res is not None:
						result = False
						break
		return result

	def is_python_prompt(self):
		""" Check if the python prompt available """
		self.device.write(b"\x0D")
		line = b""
		for i in range(6):
			data = self.device.read(1)
			if data != b"":
				line += data
		if line == b"\r\n>>> ":
			return True
		return False

	def set_date(self, date = None):
		""" Set date time in device """
		result = True
		if self.command("import machine") is None:
			year,month,day,hour,minute,second = strings.local_time(date)[:6]
			if self.command("machine.RTC().datetime((%d,%d,%d,%d,%d,%d,%d,%d))"%(year, month, day, 0, hour, minute, second, 0)) is not None:
				result = False
		return result

	def copy_file(self, in_file, target_filename):
		""" Copy file into device with target filename """
		result = True
		directory, _ = os.path.split(target_filename)
		if self.makedir(directory):
			self.print("  %s"%target_filename, end="")
			self.command("import binascii")
			self.command("import machine")
			self.command('def w(f,d,s): return f.write(binascii.a2b_base64(d)) == s')
			current_date = None
			if self.command("f=open('%s','wb')"%target_filename) is None:
				file_date = in_file.get_date_time()
				chunk = bytearray(160)
				size = in_file.get_size()
				while size > 0:
					length = in_file.readinto(chunk)
					size -= length
					part = binascii.b2a_base64(chunk[:length])
					if size <= len(chunk):
						current_date = self.command("machine.RTC().datetime()")
						year,month,day,hour,minute,second = file_date[:6]
						if self.command("machine.RTC().datetime((%d,%d,%d,%d,%d,%d,%d,%d))"%(year, month, day, 0, hour, minute, second, 0)) is not None:
							result = False
							break
					if self.command('w(f,%s,%d)'%(part, length)) is False:
						result = False
						break
				self.command("f.close()")
				if current_date is not None:
					self.command("machine.RTC().datetime(%s)"%repr(current_date))
			if result:
				self.print(" Ok")
			else:
				result = False
				self.print(" FAILED")
		else:
			result = False
			self.print("! Cannot create directory '%s'"%directory)
		return result

def get_url_filename(host, path, filename):
	""" Get the path of filename from the github releases """
	result = None
	url = "%s/%s"%(host,path)
	response = requests.get(url, allow_redirects=True)
	lines = response.content.decode("utf8").split("\n")
	for line in lines:
		if filename in line and "href" in line:
			spl = split(r'.*<a href="([a-zA-Z0-9/\.]*)".*>.*',line)
			if len(spl) > 0:
				result = spl[1]
				break
	return result

def download_last_release(host, path, filename):
	""" Download file last release of file from github """
	result = None
	try:
		filepath = get_url_filename(host, path, filename)
		if filepath is not None:
			response = requests.get(host + filepath, allow_redirects=True)
			result = response.content
	except:
		pass
	return result

def inject_zip_file(host, path, filename, serial_port, printer=None):
	""" Inject file read from github into device """
	result = None
	prompt = PythonPrompt(serial_port)
	if prompt.is_python_prompt():
		zip_file = download_last_release(host, path, filename)
		if zip_file is not None:
			with zipfile.ZipFile(io.BytesIO(zip_file),"r") as zip_ref:
				for file in zip_ref.infolist():
					file_in = ZipReader(zip_ref.read(file.filename), file.date_time)
					prompt.copy_file(file_in, file.filename)
			prompt.set_date()
			result = True
	else:
		result = False
	return result

def test():
	""" Test with server.zip """
	ports = []
	for port, a, b in sorted(list_ports.comports()):
		if not "Bluetooth" in port and not "Wireless" in port and "cu.BLTH" not in port and port != "COM1":
			ports.append(port)
	serial_port = serial.Serial(port=ports[0], baudrate=115200, timeout=1)
	while len(serial_port.read(1)) >= 1:
		pass
	serial_port.reset_input_buffer()
	inject_zip_file(GITHUB_HOST, PYCAMERESP_PATH, "server.zip", serial_port)
	serial_port.close()

if __name__ == "__main__":
	test()
