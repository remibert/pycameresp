""" Inject files read from github into device, using python prompt """
import sys
import time
import queue

import os.path
import binascii
import io
import zipfile
from re import split
import requests
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

class PromptCommand:
	""" Manage the command entered on python prompt """
	def __init__(self, command, awaited_response=None):
		""" Constructor """
		self.command = command
		self.response = None
		self.awaited_response = awaited_response

	def set_response(self, response):
		""" Set the response completed """
		self.response = response

	def get_value(self):
		""" Epurate python response """
		lines = strings.tostrings(self.response).split("\n")[1:-1]
		result = []
		for line in lines:
			try:
				result.append(eval(line.strip()))
			except:
				result.append(Exception(line.strip()))

		if len(result) == 0:
			result = None
		else:
			result = result[-1]
		return result

	def is_awaited_response(self):
		""" Indicates to the expected response """
		if self.awaited_response is None:
			return True
		elif self.awaited_response == self.get_value():
			return True
		else:
			return False

class CommandExecutor:
	""" Command executor with waiting for response """
	def __init__(self, device, printer):
		""" Constructor """
		self.device           = device
		self.commands         = queue.Queue()
		self.responses        = queue.Queue()
		self.reception_buffer = b""
		self.written_length   = 0
		self.printer = printer

	def receive(self):
		""" Receive data from device """
		# If data received
		length = self.device.get_in_waiting()
		if length > 0:
			# Add data received to reception buffer
			self.reception_buffer += self.device.read(length)

		# If one response is complete
		pos = self.reception_buffer.find(b"\r\n>>> ")
		if pos >= 0:
			# Extract response
			response = self.reception_buffer[:pos+6]

			if self.printer is not None:
				self.printer(strings.tostrings(response), end="")

			# Remove reponse from reception buffer
			self.reception_buffer = self.reception_buffer[pos + 6:]

			# If command has been placed
			if self.commands.empty() is False:
				# Set the response
				command = self.commands.get()
				command.set_response(response)

				# Push response in stack
				self.responses.put(command)

	def wait_response(self, synchrone, prompt_command):
		""" Wait response of command """
		result = None
		# If synchrone response awaited
		if synchrone:
			while True:
				# Receive response
				self.receive()

				# If a response is pending
				if self.responses.empty() is False:
					# Extract response
					prompt_response = self.responses.get()

					# Decrease the written data counter
					self.written_length -= (len(prompt_response.command) + 6)

					# Checks if the response matches the command
					if id(prompt_response) == id(prompt_command):
						# Return response
						result = prompt_response.get_value()
						break
					# checks if the response matches to the response awaited
					elif prompt_response.is_awaited_response() is False:
						raise Exception("Unexpected response")
		# Else asynchrone response awaited
		else:
			# Receive response
			self.receive()

			# If a response is pending
			if self.responses.empty() is False:
				# Extract response
				prompt_response = self.responses.get()

				# Decrease the written data counter
				self.written_length -= (len(prompt_response.command) + 6)

				# checks if the response matches to the response awaited
				if prompt_response.is_awaited_response() is False:
					raise Exception("Unexpected response")
		return result

	def execute(self, command, awaited_response=None, synchrone=False):
		""" Send command to the reception thread """
		# Flush responses if too many commands sent
		while len(command) + self.written_length >= 256:
			self.wait_response(False, None)

		# Write command
		self.device.write(b"%s\x0D"%strings.tobytes(command))

		# Calculate the written size approximately (6 is length of "\r\n>>> ")
		self.written_length += len(command) + 6

		# Create command object
		prompt_command = PromptCommand(command, awaited_response=awaited_response)

		# Adds the command to the awaiting response list
		self.commands.put(prompt_command)

		# Wait for a response if needed
		return self.wait_response(synchrone, prompt_command)

	def wait_python_prompt(self):
		""" Wait the python prompt """
		result = False
		reception_buffer = b""
		self.device.write(b"\x0D")
		for i in range(200):
			length = self.device.get_in_waiting()
			if length > 0:
				reception_buffer += self.device.read(length)
				pos = reception_buffer.find(b"\r\n>>> ")
				if pos >= 0:
					result = True
			else:
				time.sleep(0.01)
		return result

class PythonPrompt:
	""" Class to send command to python prompt """
	def __init__(self, device, printer=None, verbose=False):
		self.device = device
		# verbose = True
		self.printer  = printer
		self.executor = CommandExecutor(device, self.print if verbose else None)

	def is_python_prompt(self):
		""" Check if the python prompt available """
		return self.executor.wait_python_prompt()

	def print(self, message, end="\n"):
		""" Print message """
		if self.printer is None:
			print(message, end=end)
		else:
			self.printer(message, end)

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

		self.executor.execute("import os")
		directories.reverse()
		for d in directories:
			if d != "/":
				res = self.executor.execute("os.stat('%s')"%d, synchrone=True)
				if type(res) != type((0,)):
					res = self.executor.execute("os.mkdir('%s')"%d, synchrone=True)
					if res is not None:
						result = False
						break
		return result

	def set_date(self, date = None):
		""" Set date time in device """
		result = True
		self.executor.execute("import machine")
		year,month,day,hour,minute,second = strings.local_time(date)[:6]
		if self.executor.execute("machine.RTC().datetime((%d,%d,%d,%d,%d,%d,%d,%d))"%(year, month, day, 0, hour, minute, second, 0), synchrone=True) is not None:
			result = False
		return result

	def terminate(self):
		""" Terminate """
		self.device.write(b"\x0D")

	def copy_file(self, in_file, target_filename):
		""" Copy file into device with target filename """
		result = True

		try:
			directory, _ = os.path.split(target_filename)
			if self.makedir(directory):
				self.print("  %s "%target_filename, end="")
				self.executor.execute("import binascii")
				self.executor.execute("import machine")
				self.executor.execute('def w(f,d,s): return f.write(binascii.a2b_base64(d)) == s\r\n')
				current_date = None
				if self.executor.execute("f=open('%s','wb')"%target_filename, synchrone=True) is None:
					file_date = in_file.get_date_time()
					chunk = bytearray(160)
					size = in_file.get_size()
					while size > 0:
						length = in_file.readinto(chunk)
						if size <= len(chunk):
							current_date = self.executor.execute("machine.RTC().datetime()", synchrone=True)
							year,month,day,hour,minute,second = file_date[:6]
							if self.executor.execute("machine.RTC().datetime((%d,%d,%d,%d,%d,%d,%d,%d))"%(year, month, day, 0, hour, minute, second, 0), synchrone=True) is not None:
								result = False
								break
						size -= length
						part = binascii.b2a_base64(chunk[:length])
						if self.executor.execute('w(f,%s,%d)'%(part, length), awaited_response=True) is False:
							result = False
							break
						self.print(".",end="")
					self.executor.execute("f.close()", synchrone=True)
					if current_date is not None:
						self.executor.execute("machine.RTC().datetime(%s)"%repr(current_date), synchrone=True)
				if result:
					self.print(" Ok")
				else:
					result = False
					self.print(" FAILED")
			else:
				result = False
				self.print("! Cannot create directory '%s'"%directory)
		except Exception as err:
			result = False
			self.print(" ABORTED")
		return result

def get_url_filename(host, path, filename):
	""" Get the path of filename from the github releases """
	result = None
	url = "%s/%s"%(host,path)
	response = requests.get(url, allow_redirects=True)
	lines = response.content.decode("utf8").split("\n")
	for line in lines:
		if filename in line and "href" in line:
			spl = split(r'.*<a href="([a-zA-Z0-9/\.\-_]*)".*>.*',line)
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
					if prompt.copy_file(file_in, file.filename) is False:
						break
			prompt.set_date()
			prompt.terminate()
			result = True
	else:
		result = False
	return result

def test():
	""" Test with server.zip """
	import streamdevice
	ports = []
	for port, a, b in sorted(list_ports.comports()):
		if not "Bluetooth" in port and not "Wireless" in port and "cu.BLTH" not in port and port != "COM1":
			ports.append(port)

	serial_port = streamdevice.StreamSerial(port=ports[0], baudrate=115200, timeout=2)

	try:
		inject_zip_file(GITHUB_HOST, PYCAMERESP_PATH, "shell.zip", serial_port)

	finally:
		serial_port.close()

if __name__ == "__main__":
	test()
