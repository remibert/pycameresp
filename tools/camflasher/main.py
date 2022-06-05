#!python3
""" Tools to flash the firmware of pycameresp """
# Requirements :
#	- pip3 install serial
#	- pip3 install pyinstaller
#	- pip3 install esptool
#	- pip3 install pyserial
# For windows seven
#	- pip3 install pyqt5
# For windows 10, 11, linux, osx
#	- pip3 install pyqt6
#
# pylint:disable=no-name-in-module
import sys
import os.path
import os
import socket
import ipaddress
from pathlib import Path
from platform import uname
sys.path.append("../../modules/lib/tools")
# pylint:disable=import-error
# pylint:disable=wrong-import-position

try:
	from PyQt6 import uic
	from PyQt6.QtCore import QTimer, QEvent, Qt, QSettings, QCoreApplication
	from PyQt6.QtWidgets import QFileDialog, QColorDialog, QMainWindow, QDialog, QMenu, QApplication, QMessageBox, QErrorMessage
	from PyQt6.QtGui import QCursor,QAction,QFont,QColor
except:
	from PyQt5 import uic
	from PyQt5.QtCore import QTimer, QEvent, Qt, QSettings, QCoreApplication
	from PyQt5.QtWidgets import QFileDialog, QColorDialog, QMainWindow, QDialog, QMenu, QApplication, QMessageBox, QErrorMessage, QAction
	from PyQt5.QtGui import QCursor, QFont,QColor
from serial.tools import list_ports
from flasher import Flasher
from qstdoutvt100 import QStdoutVT100

# Settings
SETTINGS_FILENAME  = "CamFlasher.ini"
FONT_FAMILY        = "camflasher.font.family"
FONT_SIZE          = "camflasher.font.size"
WORKING_DIRECTORY  = "camflasher.working_directory"
WIN_GEOMETRY       = "camflasher.window.geometry"
FIRMWARE_FILENAMES = "camflasher.firmware.filenames"
TELNET_HOSTS       = "camflasher.telnet.host"
DEVICE_RTS_DTR     = "camflasher.device.rts_dtr"
TEXT_BACKCOLOR     = "camflasher.text.backcolor"
TEXT_FORECOLOR     = "camflasher.text.forecolor"
CURSOR_BACKCOLOR   = "camflasher.cursor.backcolor"
CURSOR_FORECOLOR   = "camflasher.cursor.textcolor"
REVERSE_BACKCOLOR  = "camflasher.reverse.backcolor"
REVERSE_FORECOLOR  = "camflasher.reverse.textcolor"
TYPE_LINK          = "camflasher.link.type"

DEFAULT_TEXT_BACKCOLOR    = QColor(0xFF,0xFA,0xE6)
DEFAULT_TEXT_FORECOLOR    = QColor(0x4D,0x47,0x00)
DEFAULT_CURSOR_BACKCOLOR  = QColor(0x64,0x5D,0x00)
DEFAULT_CURSOR_FORECOLOR  = QColor(0xFF,0xFC,0xD9)
DEFAULT_REVERSE_BACKCOLOR = QColor(0xDF,0xD9,0xA8)
DEFAULT_REVERSE_FORECOLOR = QColor(0x32,0x2D,0x00)

DOWNLOAD_VERSION = "Download the lastest version of :"

OUTPUT_TEXT = """
<html>
	<head/>
	<body style="background-color : %(text_backcolor)s">
		<p style="color : %(text_forecolor)s" >	
			def function(self):<br>
			&nbsp;&nbsp;&nbsp;&nbsp;for j in range(10):<br>
			&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print(j)<br>
			&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="background-color : %(cursor_backcolor)s;color : %(cursor_forecolor)s">#</span> &lt;- Cursor <br>
			&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="background-color : %(reverse_backcolor)s;color : %(reverse_forecolor)s"># Text in reverse video</span>
		</p>
	</body>
</html>"""

class AboutDialog(QDialog):
	""" Dialog about """
	def __init__(self, parent):
		""" Dialog box constructor """
		QDialog.__init__(self, parent)
		try:
			self.dialog = uic.loadUi('dialogabout.ui', self)
		except Exception as err:
			from dialogabout import Ui_DialogAbout
			self.dialog = Ui_DialogAbout()
			self.dialog.setupUi(self)
		self.setModal(True)

	def accept(self):
		""" Accept about dialog """
		self.close()

def get_settings():
	""" Return the QSettings class according to the os """
	if sys.platform == "darwin":
		result = QSettings()
	elif sys.platform == "win32":
		if uname() == "7":
			result = QSettings(SETTINGS_FILENAME, QSettings.IniFormat)
		else:
			result = QSettings(SETTINGS_FILENAME)
	else:
		result = QSettings()
	return result

class FlashDialog(QDialog):
	""" Dialog box to select firmware """
	def __init__(self, parent):
		""" Dialog box constructor """
		QDialog.__init__(self, parent)
		try:
			self.dialog = uic.loadUi('dialogflash.ui', self)
		except Exception as err:
			from dialogflash import Ui_DialogFlash
			self.dialog = Ui_DialogFlash()
			self.dialog.setupUi(self)
		self.initialized = False
		self.setModal(True)

	def showEvent(self, event):
		""" On window shown """
		if self.initialized is False:
			self.initialized = True
			settings = get_settings( )
			firmwares = []
			for firmware in settings.value(FIRMWARE_FILENAMES, []):
				if os.path.exists(firmware):
					firmwares.append(firmware)

			firmwares.append(DOWNLOAD_VERSION + "ESP32CAM-firmware.bin")
			firmwares.append(DOWNLOAD_VERSION + "GENERIC_SPIRAM-firmware.bin")
			firmwares.append(DOWNLOAD_VERSION + "GENERIC-firmware.bin")
			self.dialog.firmware.addItems(firmwares)
			self.dialog.firmware.setCurrentIndex(0)
			self.dialog.select_firmware.clicked.connect(self.on_firmware_clicked)
			self.dialog.baud.addItems(["9600","57600","74880","115200","230400","460800"])
			self.dialog.baud.setCurrentIndex(5)

	def save_firmwares_list(self, firmware):
		""" Save list in registry """
		settings = get_settings()
		firmwares = [firmware]
		for i in range(self.dialog.firmware.count()):
			if self.dialog.firmware.itemText(i) != self.dialog.firmware.currentText():
				firmwares.append(self.dialog.firmware.itemText(i))
		settings.setValue(FIRMWARE_FILENAMES, firmwares)

	def accept(self):
		""" Called when ok pressed """
		firmware = self.dialog.firmware.currentText()
		if  os.path.exists(firmware) or firmware[:len(DOWNLOAD_VERSION)] == DOWNLOAD_VERSION:
			self.save_firmwares_list(firmware)
			super().accept()
		elif os.path.exists(firmware) is False:
			msg = QMessageBox(parent=self)
			msg.setIcon(QMessageBox.Icon.Critical)
			msg.setText("Firmware file does not exist")
			msg.exec()

	def on_firmware_clicked(self, event):
		""" Selection of firmware button clicked """
		firmware = QFileDialog.getOpenFileName(self, caption='Select firmware file', directory=str(Path.home()),filter="Firmware files (*.bin)")
		if firmware != ('', ''):
			for i in range(self.dialog.firmware.count()):
				if self.dialog.firmware.itemText(i) == firmware[0]:
					self.dialog.firmware.setCurrentIndex(i)
					break
			else:
				self.dialog.firmware.addItem(firmware[0])
				self.dialog.firmware.setCurrentIndex(self.dialog.firmware.count()-1)

class OptionDialog(QDialog):
	""" Dialog for options """
	def __init__(self, parent):
		""" Dialog box constructor """
		QDialog.__init__(self, parent)
		try:
			self.dialog = uic.loadUi('dialogoption.ui', self)
		except Exception as err:
			from dialogoption import Ui_DialogOption
			self.dialog = Ui_DialogOption()
			self.dialog.setupUi(self)

		settings = get_settings()
		self.dialog.working_directory.setText(settings.value(WORKING_DIRECTORY,str(Path.home())))

		self.dialog.spin_font_size.setValue(int(settings.value(FONT_SIZE   ,12)))
		self.dialog.combo_font.setCurrentFont(QFont(settings.value(FONT_FAMILY ,"Courier")))
		self.text_backcolor    = settings.value(TEXT_BACKCOLOR   ,DEFAULT_TEXT_BACKCOLOR)
		self.text_forecolor    = settings.value(TEXT_FORECOLOR   ,DEFAULT_TEXT_FORECOLOR)
		self.cursor_backcolor  = settings.value(CURSOR_BACKCOLOR ,DEFAULT_CURSOR_BACKCOLOR)
		self.cursor_forecolor  = settings.value(CURSOR_FORECOLOR ,DEFAULT_CURSOR_FORECOLOR)
		self.reverse_backcolor = settings.value(REVERSE_BACKCOLOR,DEFAULT_REVERSE_BACKCOLOR)
		self.reverse_forecolor = settings.value(REVERSE_FORECOLOR,DEFAULT_REVERSE_FORECOLOR)

		self.dialog.select_directory.clicked.connect(self.on_directory_clicked)
		self.dialog.button_forecolor.clicked.connect(self.on_forecolor_clicked)
		self.dialog.button_backcolor.clicked.connect(self.on_backcolor_clicked)
		self.dialog.button_cursor_forecolor.clicked.connect(self.on_cursor_forecolor_clicked)
		self.dialog.button_cursor_backcolor.clicked.connect(self.on_cursor_backcolor_clicked)
		self.dialog.button_reverse_forecolor.clicked.connect(self.on_reverse_forecolor_clicked)
		self.dialog.button_reverse_backcolor.clicked.connect(self.on_reverse_backcolor_clicked)
		self.dialog.reset_color.clicked.connect(self.on_reset_color_clicked)

		self.dialog.combo_font.currentTextChanged.connect(self.on_font_changed)
		self.dialog.spin_font_size.valueChanged.connect(self.on_font_changed)
		self.refresh_output()
		self.setModal(True)

	def refresh_output(self):
		""" Refresh the output """
		font = QFont()
		font.setFamily    (self.dialog.combo_font.currentFont().family())
		font.setPointSize (int(self.dialog.spin_font_size.value()))
		self.dialog.label_output.setFont(font)
		# pylint:disable=possibly-unused-variable
		text_backcolor     = "rgb(%d,%d,%d)"%self.text_backcolor.getRgb()[:3]
		text_forecolor     = "rgb(%d,%d,%d)"%self.text_forecolor.getRgb()[:3]
		cursor_backcolor   = "rgb(%d,%d,%d)"%self.cursor_backcolor.getRgb()[:3]
		cursor_forecolor   = "rgb(%d,%d,%d)"%self.cursor_forecolor.getRgb()[:3]
		reverse_backcolor  = "rgb(%d,%d,%d)"%self.reverse_backcolor.getRgb()[:3]
		reverse_forecolor  = "rgb(%d,%d,%d)"%self.reverse_forecolor.getRgb()[:3]
		self.dialog.label_output.setHtml(OUTPUT_TEXT%locals())

	def on_reset_color_clicked(self):
		""" Reset the default color """
		self.text_backcolor    = DEFAULT_TEXT_BACKCOLOR
		self.text_forecolor    = DEFAULT_TEXT_FORECOLOR
		self.cursor_backcolor  = DEFAULT_CURSOR_BACKCOLOR
		self.cursor_forecolor  = DEFAULT_CURSOR_FORECOLOR
		self.reverse_backcolor = DEFAULT_REVERSE_BACKCOLOR
		self.reverse_forecolor = DEFAULT_REVERSE_FORECOLOR
		self.refresh_output()

	def on_font_changed(self, event):
		""" Font family changed """
		self.refresh_output()

	def on_directory_clicked(self, event):
		""" Selection of directory button clicked """
		settings = get_settings()
		directory = QFileDialog.getExistingDirectory(self, 'Select working directory', directory =settings.value(WORKING_DIRECTORY,str(Path.home())))
		if directory != '':
			self.dialog.working_directory.setText(directory)

	def on_forecolor_clicked(self, event):
		""" Select the forecolor """
		color = QColorDialog.getColor(parent=self, initial=self.text_forecolor, title="Text color")
		if color.isValid():
			self.text_forecolor = color
			self.refresh_output()

	def on_backcolor_clicked(self, event):
		""" Select the backcolor """
		color = QColorDialog.getColor(parent=self, initial=self.text_backcolor, title="Background color")
		if color.isValid():
			self.text_backcolor = color
			self.refresh_output()

	def on_cursor_forecolor_clicked(self, event):
		""" Select the cursor forecolor """
		color = QColorDialog.getColor(parent=self, initial=self.cursor_forecolor, title="Cursor text color")
		if color.isValid():
			self.cursor_forecolor = color
			self.refresh_output()

	def on_cursor_backcolor_clicked(self, event):
		""" Select the cursor backcolor """
		color = QColorDialog.getColor(parent=self, initial=self.cursor_backcolor, title="Cursor background color")
		if color.isValid():
			self.cursor_backcolor = color
			self.refresh_output()

	def on_reverse_forecolor_clicked(self, event):
		""" Select the reverse forecolor """
		color = QColorDialog.getColor(parent=self, initial=self.reverse_forecolor, title="Reverse text color")
		if color.isValid():
			self.reverse_forecolor = color
			self.refresh_output()

	def on_reverse_backcolor_clicked(self, event):
		""" Select the reverse backcolor """
		color = QColorDialog.getColor(parent=self, initial=self.reverse_backcolor, title="Reverse background color")
		if color.isValid():
			self.reverse_backcolor = color
			self.refresh_output()

	def accept(self):
		""" Accept about dialog """
		font = self.dialog.combo_font.currentFont()
		settings = get_settings()
		settings.setValue(FONT_FAMILY , font.family())
		settings.setValue(FONT_SIZE   , self.dialog.spin_font_size.value())
		settings.setValue(WORKING_DIRECTORY, self.dialog.working_directory.text())
		settings.setValue(TEXT_FORECOLOR   , self.text_forecolor)
		settings.setValue(TEXT_BACKCOLOR   , self.text_backcolor)
		settings.setValue(CURSOR_FORECOLOR , self.cursor_forecolor)
		settings.setValue(CURSOR_BACKCOLOR , self.cursor_backcolor)
		settings.setValue(REVERSE_FORECOLOR, self.reverse_forecolor)
		settings.setValue(REVERSE_BACKCOLOR, self.reverse_backcolor)
		super().accept()

class Ports:
	""" List of all serial ports """
	def __init__(self):
		""" Constructor """
		self.rts_dtr = {}
		self.status = {}
		self.settings = get_settings()
		self.rts_dtr = self.settings.value(DEVICE_RTS_DTR,{})
		for key in self.rts_dtr.keys():
			self.status[key] = False

	def update(self, detected_ports):
		""" Update ports with detected connected port """
		result = False
		connected = []

		# For all ports connected
		for detected_port in sorted(detected_ports):
			# If current port is usb
			if detected_port.hwid != "n/a" and detected_port.vid is not None:
				key = (detected_port.device, detected_port.vid, detected_port.pid)
				if key in self.status:
					connected.append(detected_port.device)
					if self.status[key] is False:
						self.status[key] = True
						result = True
				else:
					# Create new port
					self.status[key] = True
					self.rts_dtr[key] = False
					self.settings.setValue(DEVICE_RTS_DTR,self.rts_dtr)
					connected.append(detected_port.device)
					result = True

		# For all ports already registered
		for key in self.status:
			# For all ports connected
			for detected_port in sorted(detected_ports):
				# If port is yet connected
				if key[0] == detected_port.device and key[1] == detected_port.vid and key[2] == detected_port.pid:
					break
			else:
				# The port is disconnected
				self.status[key] = False
				result = True
		if result is True:
			return connected
		return None

	def get_rts_dtr(self, name):
		""" Get the value of rts dtr for the selected port """
		result = False
		for key in self.rts_dtr:
			if name == key[0]:
				result = self.rts_dtr[key]
				break
		return result

	def set_rts_dtr(self, name, value):
		""" Set the value of rts dtr for the selected port """
		for key in self.rts_dtr:
			if name == key[0]:
				self.rts_dtr[key] = value
				self.settings.setValue(DEVICE_RTS_DTR,self.rts_dtr)
				break

class CamFlasher(QMainWindow):
	""" Tools to flash the firmware of pycameresp """
	def __init__(self):
		""" Main window contructor """
		super(CamFlasher, self).__init__()
		self.stdout = sys.stdout
		try:
			self.window = uic.loadUi('camflasher.ui', self)
			self.geometry_ = self.window
		except Exception as err:
			from camflasher import Ui_CamFlasher
			self.window = Ui_CamFlasher()
			self.window.setupUi(self)
			self.geometry_ = self
		self.clear_selection = True
		self.title = self.windowTitle()
		self.hide_size = 0

		# Select font
		self.update_font()
		settings = get_settings()
		self.geometry_.setGeometry(settings.value(WIN_GEOMETRY, self.geometry_.geometry()))

		self.window.output.setAcceptDrops(False)
		self.window.output.setReadOnly(True)
		self.window.output.installEventFilter(self)

		self.flash_dialog = FlashDialog(self)

		# Start stdout redirection vt100 console
		self.window.output.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.window.output.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.console = QStdoutVT100(self.window.output)

		# Serial listener thread
		self.flasher = Flasher(self.stdout, settings.value(WORKING_DIRECTORY))
		self.flasher.start()
		self.current_state = None

		self.serial_ports = []

		self.port_selected = None
		self.window.combo_port.currentTextChanged.connect(self.on_port_changed)
		settings = get_settings()
		self.telnet_hosts = settings.value(TELNET_HOSTS,[])
		if self.telnet_hosts is None:
			self.telnet_hosts = []
		hosts = []
		for host, _ in self.telnet_hosts:
			if host not in hosts:
				hosts.append(host)
			if len(hosts) > 20:
				break

		self.window.combo_telnet_host.addItems(hosts)
		self.window.tabs_link.setCurrentIndex(int(settings.value(TYPE_LINK,0)))
		if len(self.telnet_hosts) > 0:
			host, port = self.telnet_hosts[0]
			self.window.edit_telnet_port.setValue(port)

		self.show()
		self.resize_console()
		self.window.output.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
		self.window.output.customContextMenuRequested.connect(self.context_menu)
		self.window.action_paste.triggered.connect(self.paste)
		self.window.action_copy.triggered.connect(self.copy)
		self.window.action_resume.setDisabled(True)
		self.window.action_flash.triggered.connect(self.on_flash_clicked)
		self.window.action_about.triggered.connect(self.on_about_clicked)
		self.window.action_option.triggered.connect(self.on_option_clicked)
		self.window.chk_rts_dtr.stateChanged.connect(self.on_rts_dtr_changed)
		self.window.action_upload_shell.triggered.connect(self.on_upload_shell)
		self.window.action_upload_server.triggered.connect(self.on_upload_server)
		self.window.tabs_link.currentChanged.connect(self.on_tabs_link_changed)
		self.window.button_telnet_connect.clicked.connect(self.on_telnet_connect)
		self.window.button_serial_open.clicked.connect(self.on_serial_open)
		self.window.combo_telnet_host.currentIndexChanged.connect(self.on_telnet_host_changed)
		self.ports = Ports()
		# Refresher of the console content
		self.timer_refresh_console = QTimer(active=True, interval=100)
		self.timer_refresh_console.timeout.connect(self.on_refresh_console)
		self.timer_refresh_console.start()

		# Refresher of the list of serial port available
		self.timer_refresh_port = QTimer(active=True, interval=1000)
		self.timer_refresh_port.timeout.connect(self.on_refresh_port)
		self.timer_refresh_port.start()

		self.window.setAcceptDrops(True)

	def update_font(self):
		""" Update console font """
		settings = get_settings()
		font = QFont()
		font.setFamily    (settings.value(FONT_FAMILY ,"Courier"))
		font.setPointSize (int(settings.value(FONT_SIZE   ,12)))
		self.window.output.setFont(font)

	def on_about_clicked(self):
		""" About menu clicked """
		about_dialog = AboutDialog(self)
		about_dialog.show()
		about_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
		about_dialog.exec()

	def context_menu(self, pos):
		""" Customization of the context menu """
		context = QMenu(self)

		copy = QAction("Copy", self)
		copy.triggered.connect(self.copy)
		context.addAction(copy)

		paste = QAction("Paste", self)
		paste.triggered.connect(self.paste)
		context.addAction(paste)

		cls = QAction("Cls", self)
		cls.triggered.connect(self.cls)
		context.addAction(cls)
		context.exec(QCursor.pos())

	def cls(self):
		""" Clear screen """
		print("\x1B[2J\x1B[1;1f",end="")

	def copy(self):
		""" Copy to clipboard the text selected """
		text_selected = self.window.output.textCursor().selectedText()
		text_selected = text_selected.replace("\xa0"," ")
		text_selected = text_selected.replace("\u2028","\n")
		QApplication.clipboard().setText(text_selected)

	def paste(self):
		""" Paste to console the content of clipboard """
		paste = QApplication.clipboard().text()
		paste = paste.replace("\n","\r")
		paste = paste.encode("utf-8")
		self.flasher.send_key(paste)

	def eventFilter(self, obj, event):
		""" Treat key pressed on console """
		if event.type() == QEvent.Type.KeyPress:
			key = self.console.convert_key_to_vt100(event)
			if key is not None:
				self.clear_selection = True
				self.flasher.send_key(key)
			return True
		return super(CamFlasher, self).eventFilter(obj, event)

	def resize_console(self):
		""" Resize console """
		# Save the position
		settings = get_settings()
		geometry = self.geometry_.geometry()
		settings.setValue(WIN_GEOMETRY, geometry)
		self.console.set_color(
			settings.value(TEXT_BACKCOLOR,    DEFAULT_TEXT_BACKCOLOR),
			settings.value(TEXT_FORECOLOR,    DEFAULT_TEXT_FORECOLOR),
			settings.value(CURSOR_BACKCOLOR,  DEFAULT_CURSOR_BACKCOLOR),
			settings.value(CURSOR_FORECOLOR,  DEFAULT_CURSOR_FORECOLOR),
			settings.value(REVERSE_BACKCOLOR, DEFAULT_REVERSE_BACKCOLOR),
			settings.value(REVERSE_FORECOLOR, DEFAULT_REVERSE_FORECOLOR))

		# Calculate the dimension in pixels of a text of 200 lines with 200 characters
		line = "W"*200 + "\n"
		line = line*200
		line = line[:-1]
		size = self.window.output.fontMetrics().size(Qt.TextFlag.TextWordWrap,line)

		# Deduce the size of console visible in the window
		width  = (self.window.output.contentsRect().width()  * 200)// size.width() -  2
		height = int((self.window.output.contentsRect().height() * 200)/ size.height() - 0.3)

		self.hide_size = 0
		self.setWindowTitle("%s %dx%d"%(self.title, width, height))
		self.console.set_size(width, height)

	def moveEvent(self, _):
		""" Treat the window move event"""
		self.resize_console()

	def resizeEvent(self, _):
		""" Treat the window resize event """
		self.resize_console()

	def on_tabs_link_changed(self):
		""" The links tab has changed """
		settings = get_settings()
		settings.setValue(TYPE_LINK,self.window.tabs_link.currentIndex())
		if self.window.tabs_link.currentIndex() == 1 and self.current_state == self.flasher.DISCONNECTED:
			self.window.combo_telnet_host.setFocus()
		else:
			self.window.output.setFocus()

	def on_upload_server(self):
		""" On menu upload server clicked """
		self.upload_from_server("server.zip")

	def on_upload_shell(self):
		""" On menu upload shell clicked """
		self.upload_from_server("shell.zip")

	def upload_from_server(self, filename):
		""" Upload file from pycameresp github into device """
		msg = QMessageBox(parent=self)
		msg.setIcon(QMessageBox.Icon.Question)
		msg.setStandardButtons(QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
		msg.setText("Do you want to upload the latest version of %s from pycameresp github into the device"%filename)
		if msg.exec() == QMessageBox.StandardButton.Yes:
			self.flasher.upload_from_server(filename)

	def dragEnterEvent(self, e):
		""" Drag enter event received """
		self.dragMoveEvent(e)

	def dragMoveEvent(self, e):
		""" Drag move event received """
		if e.mimeData().hasUrls():
			e.accept()
		else:
			e.ignore()

	def dropEvent(self, e):
		if e.mimeData().hasUrls():
			filenames = []


			zip_detected = False
			for file in e.mimeData().urls():
				filename = file.toLocalFile()
				if os.path.splitext(filename)[1].lower() == ".zip":
					zip_detected = True
				filenames.append(filename)

			zip_extract = False
			if zip_detected:
				msg = QMessageBox(parent=self)
				msg.setIcon(QMessageBox.Icon.Question)
				msg.setStandardButtons(QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
				msg.setText("Do you want to extract the contents of the zip in the device ?")
				if msg.exec() == QMessageBox.StandardButton.Yes:
					zip_extract = True

			self.flasher.upload_files((filenames, zip_extract))
			self.show()
			getattr(self, "raise")()
			self.activateWindow()

	def on_option_clicked(self):
		""" On option menu clicked """
		option_dialog = OptionDialog(self)
		option_dialog.show()
		option_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
		result = option_dialog.exec()
		if result == 1:
			settings = get_settings()
			self.flasher.set_directory(settings.value(WORKING_DIRECTORY,str(Path.home())))
			self.update_font()
			self.resize_console()

	def on_refresh_port(self):
		""" Refresh the combobox content with the serial ports detected """
		# self.console.test()
		self.hide_size += 1
		if self.hide_size > 3:
			self.setWindowTitle(self.title)

		ports_connected = self.ports.update(list_ports.comports())
		if ports_connected is not None:
			for i in range(self.window.combo_port.count()):
				if not self.window.combo_port.itemText(i) in ports_connected:
					self.window.combo_port.removeItem(i)

			for port in ports_connected:
				for i in range(self.window.combo_port.count()):
					if self.window.combo_port.itemText(i) == port:
						break
				else:
					self.window.combo_port.addItem(port)

	def set_state_serial(self):
		""" Set serial state """
		# Serial config
		if self.current_state == self.flasher.DISCONNECTED:
			self.window.combo_port.setEnabled(True)
			self.window.chk_rts_dtr.setEnabled(True)
		else:
			self.window.combo_port.setEnabled(False)
			self.window.chk_rts_dtr.setEnabled(False)

		# Serial open button
		if self.current_state == self.flasher.SERIAL_CONNECTED:
			self.window.button_serial_open.setText("Close")
			self.window.button_serial_open.setEnabled(True)
		else:
			self.window.button_serial_open.setText("Open")
			if self.current_state == self.flasher.DISCONNECTED:
				self.window.button_serial_open.setEnabled(True)
			else:
				self.window.button_serial_open.setEnabled(False)

	def set_state_menu(self):
		""" Set menu state """
		# Flash menu
		if self.current_state in [self.flasher.TELNET_CONNECTED, self.flasher.CONNECTING_TELNET, self.flasher.FLASHING]:
			self.window.action_flash.setEnabled(False)
		else:
			self.window.action_flash.setEnabled(True)

		# Upload menus
		if self.current_state in [self.flasher.TELNET_CONNECTED, self.flasher.SERIAL_CONNECTED]:
			self.window.action_upload_server.setEnabled(True)
			self.window.action_upload_shell.setEnabled(True)
		else:
			self.window.action_upload_server.setEnabled(False)
			self.window.action_upload_shell.setEnabled(False)

	def set_state_telnet(self):
		""" Set telnet state """
		# Config telnet
		if self.current_state == self.flasher.DISCONNECTED:
			self.window.combo_telnet_host.setEnabled(True)
			self.window.edit_telnet_port.setEnabled(True)
			self.window.combo_telnet_host.setFocus()
		else:
			self.window.combo_telnet_host.setEnabled(False)
			self.window.edit_telnet_port.setEnabled(False)
			self.window.output.setFocus()

		# Button telnet connect
		if self.current_state == self.flasher.DISCONNECTED:
			self.window.button_telnet_connect.setText("Connect")
			self.window.button_telnet_connect.setEnabled(True)
		elif self.current_state == self.flasher.CONNECTING_TELNET:
			self.window.button_telnet_connect.setText("Cancel")
			self.window.button_telnet_connect.setEnabled(True)
		elif self.current_state == self.flasher.TELNET_CONNECTED:
			self.window.button_telnet_connect.setText("Disconnect")
			self.window.button_telnet_connect.setEnabled(True)
		elif self.current_state in [self.flasher.SERIAL_CONNECTED, self.flasher.FLASHING]:
			self.window.button_telnet_connect.setText("Connect")
			self.window.button_telnet_connect.setEnabled(False)

	def connection_state(self):
		""" Manage the connection state """
		state = self.flasher.get_state()
		if state != self.current_state:
			self.current_state = state
			self.set_state_menu()
			self.set_state_serial()
			self.set_state_telnet()

	def on_telnet_host_changed(self, event):
		""" Event combo telnet host changed """
		for host, port in self.telnet_hosts:
			if host == self.window.combo_telnet_host.currentText():
				self.window.edit_telnet_port.setValue(port)

	def on_telnet_connect(self, event):
		""" Click on telnet button connection """
		if self.flasher.get_state() == self.flasher.DISCONNECTED:
			full_host = self.window.combo_telnet_host.currentText()
			if " " in full_host:
				host = full_host.split(" ")[0]
			else:
				host = full_host
			port  = self.window.edit_telnet_port.value()
			if len(host) > 0:
				validated = False
				try:
					ipaddress.ip_network(host)
					validated = True
				except:
					pass

				if validated is False:
					try:
						res = socket.gethostbyaddr(host)
						if len(res) == 3:
							validated = True
					except:
						pass

				if validated:
					new_telnet_hosts = [[full_host, port]]
					for full_h,p  in self.telnet_hosts:
						if " " in full_h:
							h = full_h.split(" ")[0]
						else:
							h = full_h
						if h != host:
							new_telnet_hosts.append([full_h,p])
						elif len(new_telnet_hosts) > 20:
							break
					self.telnet_hosts = new_telnet_hosts
					self.refresh_combo_telnet()
					self.flasher.connect_telnet(host,port)
				else:
					print("Invalid host ip address '%s:%d'"%(host,port))
			else:
				host_to_remove = self.window.combo_telnet_host.itemText(self.window.combo_telnet_host.currentIndex())

				new_telnet_hosts = []
				for h,p  in self.telnet_hosts:
					if h != host_to_remove:
						new_telnet_hosts.append([h,p])
				self.telnet_hosts = new_telnet_hosts
				self.refresh_combo_telnet()
				self.window.combo_telnet_host.setFocus()
		else:
			self.flasher.disconnect()

	def on_serial_open(self, event):
		""" Click on open serial button"""
		if self.flasher.get_state() == self.flasher.DISCONNECTED:
			rts_dtr = self.ports.get_rts_dtr(self.get_port())
			self.window.chk_rts_dtr.setChecked(rts_dtr)
			self.flasher.connect_serial(port = self.get_port(), rts_dtr=rts_dtr)
		else:
			self.flasher.disconnect()

	def refresh_combo_telnet(self):
		""" Refresh the telnet combobox """
		hosts = []
		for host, _ in self.telnet_hosts:
			if host not in hosts:
				hosts.append(host)
		settings = get_settings()
		self.window.combo_telnet_host.clear()
		self.window.combo_telnet_host.addItems(hosts)
		settings.setValue(TELNET_HOSTS, self.telnet_hosts)

	def on_rts_dtr_changed(self, event):
		""" On change of DTR/STR check box """
		rts_dtr = self.window.chk_rts_dtr.isChecked()
		self.ports.set_rts_dtr(self.get_port(), rts_dtr)

	def on_port_changed(self, event):
		""" On port changed event """
		rts_dtr = self.ports.get_rts_dtr(self.get_port())
		self.window.chk_rts_dtr.setChecked(rts_dtr)
		if self.window.tabs_link.currentIndex() == 0:
			self.flasher.connect_serial(port=self.get_port(), rts_dtr=rts_dtr)

	def on_flash_clicked(self, event):
		""" Flash of firmware button clicked """
		self.flash_dialog.show()
		self.flash_dialog.dialog.erase.setChecked(False)
		self.flash_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
		result = self.flash_dialog.exec()
		if result == 1 and self.window.combo_port.currentText() != "":
			try:
				firmware = self.flash_dialog.dialog.firmware.currentText()
				if firmware[:len(DOWNLOAD_VERSION)] == DOWNLOAD_VERSION:
					firmware = (firmware[len(DOWNLOAD_VERSION):],)
				port      = self.window.combo_port.currentText()
				baud      = self.flash_dialog.dialog.baud.currentText()
				rts_dtr   = self.window.chk_rts_dtr.isChecked()
				erase     = self.flash_dialog.dialog.erase.isChecked()
				self.flasher.flash(port, baud, rts_dtr, firmware, erase)
			except Exception as err:
				print(err)

	def get_port(self):
		""" Get the name of serial port """
		try:
			result = self.window.combo_port.currentText()
		except:
			result = None
		return result

	def on_refresh_console(self):
		""" Refresh the console content """
		self.connection_state()

		self.window.output.viewport().setProperty("cursor", QCursor(Qt.CursorShape.ArrowCursor))
		if self.clear_selection is True:
			cursor = self.window.output.textCursor()
			cursor.removeSelectedText()
			self.clear_selection = False

		cursor = self.window.output.textCursor()
		if cursor.selectionEnd() == cursor.selectionStart():
			output = self.console.refresh()
			if output != "":
				self.flasher.send_key(output.encode("utf-8"))

	def closeEvent(self, event):
		""" On close window event """
		# Terminate stdout redirection
		self.console.close()

		# Stop serial thread
		self.flasher.quit()

def except_hook(cls, exception, traceback):
	""" Exception hook """
	from traceback import extract_tb
	msg = QErrorMessage()
	msg.setModal(True)
	text = '<code>' + str(exception) + "<br>"
	for filename, line, method, content in extract_tb(traceback) :
		text += '&nbsp;&nbsp;&nbsp;&nbsp;<FONT COLOR="#ff0000">File "%s", line %d, in %s</FONT><br>'%(filename,line,method)
		text += '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;%s<br>'%(content)
	text += "</code>"
	msg.resize(800, 400)
	msg.showMessage(text)
	msg.exec()
	sys.__excepthook__(cls, exception, traceback)

def main():
	""" Main application """
	QCoreApplication.setApplicationName("CamFlasher")
	QCoreApplication.setOrganizationName("pycameresp")
	QCoreApplication.setOrganizationDomain("https://github.com/remibert/pycameresp")
	app = QApplication(sys.argv)
	sys.excepthook = except_hook
	window = CamFlasher()
	app.exec()

if __name__ == "__main__":
	main()
