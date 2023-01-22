#!/usr/bin/python3
# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Tools to flash the firmware of pycameresp """
# Requirements :
#	- pip3 install pyinstaller
#	- pip3 install esptool
#	- pip3 install pyserial
#	- pip3 install requests
# For windows seven
#	- pip3 install pyqt5
# For windows 10, 11, linux, osx
#	- pip3 install pyqt6
#
# pylint:disable=consider-using-f-string
# pylint:disable=no-name-in-module
import sys
import os.path
import os
import socket
import ipaddress
import copy
import vt100
import settings

sys.path.append("../../modules/lib/tools")
# pylint:disable=import-error
# pylint:disable=wrong-import-position

try:
	from PyQt6 import uic
	from PyQt6.QtCore import QTimer, QEvent, Qt, QCoreApplication
	from PyQt6.QtWidgets import QMainWindow, QMenu, QApplication, QMessageBox, QErrorMessage
	from PyQt6.QtGui import QCursor,QAction,QFont
except:
	from PyQt5 import uic
	from PyQt5.QtCore import QTimer, QEvent, Qt, QCoreApplication
	from PyQt5.QtWidgets import QMainWindow, QMenu, QApplication, QMessageBox, QErrorMessage, QAction
	from PyQt5.QtGui import QCursor, QFont

from dialogs import *
from serial.tools import list_ports
from flasher import Flasher
from qstdoutvt100 import QStdoutVT100

class Ports:
	""" List of all serial ports """
	def __init__(self):
		""" Constructor """
		self.rts_dtr = {}
		self.status = {}
		self.config = settings.get_settings()
		self.rts_dtr = self.config.value(settings.DEVICE_RTS_DTR,{})
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
						pass
				else:
					# Create new port
					self.status[key] = True
					self.rts_dtr[key] = False
					self.config.setValue(settings.DEVICE_RTS_DTR,self.rts_dtr)
					connected.append(detected_port.device)
					result = True
			else:
				pass

		# For all ports already registered
		for key in self.status:
			# For all ports connected
			for detected_port in sorted(detected_ports):
				# If port is yet connected
				if key[0] == detected_port.device and key[1] == detected_port.vid and key[2] == detected_port.pid:
					result = True
					break
				else:
					pass
			else:
				# The port is disconnected
				self.status[key] = False
				result = True
		if result is True:
			return connected
		else:
			pass
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
				self.config.setValue(settings.DEVICE_RTS_DTR,self.rts_dtr)
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
		self.paused = False
		# Select font
		self.update_font()
		config_ = settings.get_settings()
		self.geometry_.setGeometry(config_.value(settings.WIN_GEOMETRY, self.geometry_.geometry()))

		self.window.output.setAcceptDrops(False)
		self.window.output.setReadOnly(True)
		self.window.output.installEventFilter(self)

		self.flash_dialog = FlashDialog(self)

		# Start stdout redirection vt100 console
		self.window.output.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.window.output.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.console = QStdoutVT100(self.window.output)

		# Serial listener thread
		self.flasher = Flasher(self.stdout, config_.value(settings.WORKING_DIRECTORY))
		self.flasher.start()
		self.current_state = None

		self.port_selected = None
		self.ports_connected = None
		self.window.combo_port.currentTextChanged.connect(self.on_port_changed)

		self.telnet_hosts = config_.value(settings.TELNET_HOSTS,[])
		if self.telnet_hosts is None:
			self.telnet_hosts = []
		hosts = []
		for host, _ in self.telnet_hosts:
			if host not in hosts:
				hosts.append(host)
			if len(hosts) > 20:
				break

		self.window.combo_telnet_host.addItems(hosts)
		self.window.tabs_link.setCurrentIndex(int(config_.value(settings.TYPE_LINK,0)))
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
		self.window.action_pause.triggered.connect(self.pause)
		self.window.action_resume.triggered.connect(self.pause)
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
		self.selected_text = None

	def update_font(self):
		""" Update console font """
		config_ = settings.get_settings()
		font = QFont()
		font.setFamily    (config_.value(settings.FONT_FAMILY ,"Courier"))
		font.setPointSize (int(config_.value(settings.FONT_SIZE   ,12)))
		self.window.output.setFont(font)

	def on_about_clicked(self):
		""" About menu clicked """
		about_dialog = AboutDialog(self)
		about_dialog.show()
		about_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
		about_dialog.exec()

	def context_menu(self, pos):
		""" Customization of the context menu """
		self.console.reset_pressed()
		context = QMenu(self)

		copy_ = QAction("Copy", self)
		copy_.triggered.connect(self.copy)
		context.addAction(copy_)

		if self.paused is False:
			paste = QAction("Paste", self)
			paste.triggered.connect(self.paste)
			context.addAction(paste)

			cls = QAction("Cls", self)
			cls.triggered.connect(self.cls)
			context.addAction(cls)

			pause = QAction("Pause", self)
			pause.triggered.connect(self.pause)
			context.addAction(pause)
		else:
			pause = QAction("Resume", self)
			pause.triggered.connect(self.pause)
			context.addAction(pause)

		context.exec(QCursor.pos())

	def pause(self):
		""" Pause console display """
		self.paused = not self.paused
		if self.paused:
			self.window.action_paste.setDisabled(True)
			self.window.action_pause.setDisabled(True)
			self.window.action_resume.setEnabled(True)
		else:
			self.window.action_pause.setEnabled(True)
			self.window.action_paste.setEnabled(True)
			self.window.action_resume.setDisabled(True)

	def cls(self):
		""" Clear screen """
		self.cancel_selection()
		print("\x1B[2J\x1B[1;1f",end="")

	def get_selected_text(self):
		""" Get the selected text """
		text_selected = self.window.output.textCursor().selectedText()
		text_selected = text_selected.replace("\xa0"," ")
		text_selected = text_selected.replace("\u2028","\n")
		return text_selected

	def copy(self):
		""" Copy to clipboard the text selected """
		if self.console.is_in_editor():
			selected = self.selected_text
		else:
			selected = self.get_selected_text()
		if selected is not None:
			if self.console.is_in_editor():
				self.flasher.send_key(b"\x03")
			QApplication.clipboard().setText(selected)

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
				if self.paused is False:
					if self.console.is_in_editor() and self.selected_text is not None:
						# If key is cut
						if key == b'\x18':
							QApplication.clipboard().setText(self.selected_text)
							self.selected_text = None
						# If key is paste
						elif key == b'\x19':
							pass
						# If key is copy
						elif key == b'\x03':
							QApplication.clipboard().setText(self.selected_text)
							self.selected_text = None
						else:
							self.selected_text = None
					self.flasher.send_key(key)
			return True
		return super(CamFlasher, self).eventFilter(obj, event)

	def resize_console(self):
		""" Resize console """
		# Save the position
		config_ = settings.get_settings()
		geometry = self.geometry_.geometry()
		config_.setValue(settings.WIN_GEOMETRY, geometry)

		colors = config_.value(settings.FIELD_COLORS, copy.deepcopy(vt100.DEFAULT_COLORS))
		self.console.set_colors(colors)

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
		config_ = settings.get_settings()
		config_.setValue(settings.TYPE_LINK,self.window.tabs_link.currentIndex())
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
		""" Drop event received """
		self.show()
		getattr(self, "raise")()
		self.activateWindow()
		if e.mimeData().hasUrls():
			filenames = []
			zip_detected = False
			for file in e.mimeData().urls():
				filename = file.toLocalFile()
				if os.path.splitext(filename)[1].lower() == ".zip":
					zip_detected = True
				if filename.strip() != "":
					filenames.append(filename.strip())

			if len(filenames) > 0:
				zip_extract = False
				if zip_detected:
					msg = QMessageBox(parent=self)
					msg.setIcon(QMessageBox.Icon.Question)
					msg.setStandardButtons(QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
					msg.setText("Do you want to extract the contents of the zip in the device ?")
					if msg.exec() == QMessageBox.StandardButton.Yes:
						zip_extract = True

				self.flasher.upload_files((filenames, zip_extract))

	def on_option_clicked(self):
		""" On option menu clicked """
		option_dialog = OptionDialog(self)
		option_dialog.show()
		option_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
		result = option_dialog.exec()
		if result == 1:
			config_ = settings.get_settings()
			self.flasher.set_directory(config_.value(settings.WORKING_DIRECTORY,str(Path.home())))
			self.update_font()
			self.resize_console()

	def on_refresh_port(self):
		""" Refresh the combobox content with the serial ports detected """
		# self.console.test()

		self.hide_size += 1
		if self.hide_size > 3:
			self.setWindowTitle(self.title)

		self.ports_connected = self.ports.update(list_ports.comports())
		if self.ports_connected is not None:
			for i in range(self.window.combo_port.count()):
				if not self.window.combo_port.itemText(i) in self.ports_connected:
					self.window.combo_port.removeItem(i)

			for port in self.ports_connected:
				for i in range(self.window.combo_port.count()):
					if self.window.combo_port.itemText(i) == port:
						break
				else:
					self.window.combo_port.addItem(port)

		# Flash menu
		if self.ports_connected is None or self.ports_connected == [] or \
			self.current_state in [self.flasher.TELNET_CONNECTED, self.flasher.CONNECTING_TELNET, self.flasher.FLASHING]:
			self.window.action_flash.setEnabled(False)
		else:
			self.window.action_flash.setEnabled(True)

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
		self.cancel_selection()
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
		self.cancel_selection()
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
		config_ = settings.get_settings()
		self.window.combo_telnet_host.clear()
		self.window.combo_telnet_host.addItems(hosts)
		config_.setValue(settings.TELNET_HOSTS, self.telnet_hosts)

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
				if self.paused:
					self.pause()
				firmware = self.flash_dialog.dialog.firmware.currentText()
				if firmware[:len(DOWNLOAD_VERSION)] == DOWNLOAD_VERSION:
					firmware = (firmware[len(DOWNLOAD_VERSION):],)
				port      = self.window.combo_port.currentText()
				baud      = self.flash_dialog.dialog.baud.currentText()
				rts_dtr   = self.window.chk_rts_dtr.isChecked()
				erase     = self.flash_dialog.dialog.erase.isChecked()
				address   = self.flash_dialog.dialog.address.currentText()
				chip      = self.flash_dialog.dialog.chip.currentText()
				self.cancel_selection()
				self.flasher.flash((port, baud, rts_dtr, firmware, erase, address, chip))
			except Exception as err:
				print(err)

	def get_port(self):
		""" Get the name of serial port """
		try:
			result = self.window.combo_port.currentText()
		except:
			result = None
		return result

	def cancel_selection(self):
		""" Cancel the text selected """
		cursor = self.window.output.textCursor()
		text = cursor.selectedText()
		cursor.removeSelectedText()
		cursor.insertText(text)
		self.clear_selection = False

	def on_refresh_console(self):
		""" Refresh the console content """
		self.connection_state()

		self.window.output.viewport().setProperty("cursor", QCursor(Qt.CursorShape.ArrowCursor))
		cursor = self.window.output.textCursor()
		if self.clear_selection is True:
			self.cancel_selection()

		if self.console.is_select_in_editor():
			move, selection = self.console.get_selection()
			move = move.encode("utf-8")
			if selection is True:
				self.selected_text = self.get_selected_text()
			else:
				self.selected_text = None
			# self.stdout.write("%s\n"%move)
			self.flasher.send_key(move)
			self.cancel_selection()

		# Refresh only if mouse is not in selection or if the console is not paused
		if   cursor.hasSelection()         is False and \
			self.paused                    is False:
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
