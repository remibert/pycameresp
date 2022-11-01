# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Inject files read from github into device, using python prompt """
import sys
import time
import tempfile
import queue
import os.path
import binascii
import io
import zipfile
import requests
from serial.tools import list_ports
sys.path.append("../../modules/lib/tools")
# pylint:disable=consider-using-f-string
# pylint:disable=import-error
# pylint:disable=wrong-import-position
import filesystem
import strings
import streamdevice
import vt100

GITHUB_API_HOST = 'https://api.github.com/repos'
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
		self.waiting_counter = 0
		self.written_length   = 0
		self.printer = printer

	def print(self, message, end="\n"):
		""" Print message """
		if self.printer is None:
			print(message, end=end)
		else:
			self.printer(message, end)

	def receive(self):
		""" Receive data from device """
		# If data received
		length = self.device.get_in_waiting()
		if length > 0:
			# Add data received to reception buffer
			self.reception_buffer += self.device.read(length)
			self.waiting_counter = 0
		else:
			self.waiting_counter += 1
			time.sleep(0.01)

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
		if self.waiting_counter > 100:
			self.waiting_counter = self.waiting_counter
			raise Exception("Not response")

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

	def wait_prompt(self):
		""" Wait the prompt """
		result = ""
		reception_buffer = b""
		self.device.write(b"\x0D")
		for i in range(10):
			length = self.device.get_in_waiting()
			if length > 0:
				reception_buffer += self.device.read(length)
				pos = reception_buffer.find(b"\r\n>>> ")
				if pos >= 0:
					result = ">>>"
					break
			else:
				time.sleep(0.1)
				if reception_buffer.find(b"=> ") > 0:
					result = "=>"
					break
				elif len(reception_buffer) >= 6:
					break
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
		return self.executor.wait_prompt() == ">>>"

	def wait_prompt(self):
		""" Wait the prompt """
		return self.executor.wait_prompt()

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

	def copy_file(self, in_file, device_filename):
		""" Copy file into device with target filename """
		result = True

		directory, _ = os.path.split(device_filename)
		if self.makedir(directory):
			progression = 0
			self.executor.execute("import binascii")
			self.executor.execute("import machine")
			self.executor.execute('def w(f,d,s): return f.write(binascii.a2b_base64(d)) == s\r\n')
			current_date = None
			if self.executor.execute("f=open('%s','wb')"%device_filename, synchrone=True) is None:
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
					self.print("\r  %-40s %s"%(device_filename, ["|","/","-","\\"][progression%4]), end="")
					progression += 1

				self.executor.execute("f.close()", synchrone=True)
				if current_date is not None:
					self.executor.execute("machine.RTC().datetime(%s)"%repr(current_date), synchrone=True)
			if result:
				self.print("\r  %-40s OK  "%device_filename)
			else:
				result = False
				self.print("\r  %-40s FAILED  "%device_filename)
		else:
			result = False
			self.print("! Cannot create directory '%s'"%directory)
		return result

class PythonUploader:
	""" Upload file with python prompt """
	def __init__(self,  printer=None):
		""" Constructor """
		self.printer = printer
		self.prompt = None

	def print(self, message, end="\n"):
		""" Print message """
		if self.printer is None:
			print(message, end)
		else:
			self.printer(message, end)

	def get_url_filename(self, host, path, filename):
		""" Get the path of filename from the github releases """
		result = None
		url = "%s/%s"%(host,path)
		response = requests.get(url, allow_redirects=True, timeout=10)
		for version in response.json():
			for asset in version["assets"]:
				if asset["name"] == filename:
					if result is None:
						result = asset["browser_download_url"]
		return result

	def upload_from_server(self, device, api_host, path, filename):
		""" Upload file """
		if self.check_prompt(device):
			zip_file = self.download_last_release(api_host, path, filename)
			zip_content = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
			zip_content.write(zip_file)
			zip_content.close()
			try:
				self.upload_zip(device, zip_content.name)
			finally:
				os.unlink(zip_content.name)

	def upload_zip(self, device, zip_filename):
		""" Upload all files contained in zip """
		if self.check_prompt(device):
			self.print(vt100.COLOR_OK+"Upload to device start"+vt100.COLOR_NONE)
			result = self.prompt_uploader(device, [zip_filename], zip_extract=True)
			self.display_result(result)

	def prompt_uploader(self, device, filenames, directory="", zip_extract=False):
		""" Upload file directly on python prompt """
		result = False
		if self.check_prompt(device):
			try:
				for filename in filenames:
					result = True
					# If the content of zip must be extracted
					if zip_extract and os.path.splitext(filename)[1].lower() == ".zip":
						with zipfile.ZipFile(filename,"r") as zip_file:
							for file in zip_file.infolist():
								file_in = ZipReader(zip_file.read(file.filename), file.date_time)
								if self.prompt.copy_file(file_in, file.filename) is False:
									result = False
									break
					else:
						if directory != "":
							device_filename = filename[len(directory)+1:]
						else:
							device_filename = filename
						in_file = BinaryReader(filename)
						if self.prompt.copy_file(in_file, device_filename) is False:
							result = False
							break
					if result is False:
						break
			except Exception as err:
				result = False
		return result

	def upload_files(self, device, filenames, directory="", zip_extract=False):
		""" Upload all files contained in zip """
		if self.check_prompt(device):
			self.print(vt100.COLOR_OK+"Upload to device start"+vt100.COLOR_NONE)
			result = self.prompt_uploader(device, filenames=filenames, directory=directory, zip_extract=zip_extract)
			self.display_result(result)

	def wait_prompt(self, device):
		""" Get the current prompt """
		self.prompt = PythonPrompt(device)
		return self.prompt.wait_prompt()

	def check_prompt(self, device):
		""" Check the python prompt """
		result = False
		self.prompt = PythonPrompt(device)
		if self.prompt.is_python_prompt() is False:
			self.print(vt100.COLOR_FAILED+"Prompt python not available"+vt100.COLOR_NONE)
		else:
			result = True
		return result

	def display_result(self, state):
		""" Display the upload result """
		if state is True:
			self.prompt.set_date()
			self.print(vt100.COLOR_OK+"Upload success"+vt100.COLOR_NONE)
		else:
			self.print(vt100.COLOR_FAILED+"Upload failed"+vt100.COLOR_NONE)
		self.prompt.terminate()

	def download_last_release(self, api_host, path, filename):
		""" Download file last release of file from github """
		result   = None
		filepath = None
		try:
			self.print("\n"+vt100.COLOR_OK+"Find the latest version of %s"%filename+vt100.COLOR_NONE)
			filepath = self.get_url_filename(api_host, path, filename)
		except Exception as err:
			self.print(vt100.COLOR_FAILED+"Unable to find the latest version"+vt100.COLOR_NONE)

		if filepath is not None:
			try:
				self.print(vt100.COLOR_OK+"Download %s"%filepath+vt100.COLOR_NONE)
				response = requests.get(filepath, allow_redirects=True, timeout=10)
				result = response.content
			except Exception as err:
				self.print(vt100.COLOR_FAILED+"Download failed"+vt100.COLOR_NONE)
		return result

def test():
	""" Test with server.zip """
	ports = []
	for port, a, b in sorted(list_ports.comports()):
		if not "Bluetooth" in port and not "Wireless" in port and "cu.BLTH" not in port and port != "COM1":
			ports.append(port)

	serial_port = streamdevice.StreamSerial(port=ports[0], baudrate=115200, timeout=2)

	try:
		uploader = PythonUploader(print)
		uploader.upload_from_server(serial_port, GITHUB_API_HOST, PYCAMERESP_PATH, "shell.zip")
	finally:
		serial_port.close()

if __name__ == "__main__":
	test()
