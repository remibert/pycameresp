#!/usr/bin/python3
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
try:
	from PyQt6 import uic
	from PyQt6.QtCore import QTimer, QEvent, Qt
	from PyQt6.QtWidgets import QFileDialog, QMainWindow, QDialog, QMenu, QApplication, QMessageBox
	from PyQt6.QtGui import QCursor,QAction
except:
	from PyQt5 import uic
	from PyQt5.QtCore import QTimer, QEvent, Qt
	from PyQt5.QtWidgets import QFileDialog, QMainWindow, QDialog, QMenu, QApplication, QMessageBox, QAction
	from PyQt5.QtGui import QCursor
from serial.tools import list_ports
from flasher import Flasher
from qstdoutvt100 import QStdoutVT100

# Main keys
main_keys = {
	Qt.Key.Key_Escape    : b'\x1b',
	Qt.Key.Key_Tab       : b'\t',
	Qt.Key.Key_Backtab   : b'\x1b[Z',
	Qt.Key.Key_Backspace : b'\x7f',
	Qt.Key.Key_Return    : b'\r',
	Qt.Key.Key_Delete    : b'\x1b[3~',
	Qt.Key.Key_Enter     : b"\x03", # Control C, why it is Key_Enter ????
}

# Function keys
function_keys = {
	Qt.Key.Key_F1        : [b'\x1bOP'  ,b'\x1b[1;2P'],
	Qt.Key.Key_F2        : [b'\x1bOQ'  ,b'\x1b[1;2Q'],
	Qt.Key.Key_F3        : [b'\x1bOR'  ,b'\x1b[1;2R'],
	Qt.Key.Key_F4        : [b'\x1bOS'  ,b'\x1b[1;2S'],
	Qt.Key.Key_F5        : [b'\x1b[15~',b'\x1b[15;2~'],
	Qt.Key.Key_F6        : [b'\x1b[17~',b'\x1b[17;2~'],
	Qt.Key.Key_F6        : [b'\x1b[18~',b'\x1b[18;2~'],
	Qt.Key.Key_F8        : [b'\x1b[19~',b'\x1b[19;2~'],
	Qt.Key.Key_F9        : [b'\x1b[20~',b'\x1b[20;2~'],
	Qt.Key.Key_F10       : [b'\x1b[21~',b'\x1b[21;2~'],
	Qt.Key.Key_F11       : [b'\x1b[23~',b'\x1b[23;2~'],
	Qt.Key.Key_F12       : [b'\x1b[24~',b'\x1b[24;2~'],
}

# Arrow keys, page up and down, home and end
move_keys = {
	#                        Nothing   Shift        Meta         Alt            Control    Shift+Alt    Shift+Meta   Shift+Control
	Qt.Key.Key_Up        : [b'\x1b[A' ,b'\x1b[1;2A',b'\x1b[1;5A',b'\x1b\x1b[A' ,b'\x1b[A' ,b'\x1b[1;2A',b'\x1b[1;6A',b'\x1b[1;6A'],
	Qt.Key.Key_Down      : [b'\x1b[B' ,b'\x1b[1;2B',b'\x1b[1;5B',b'\x1b\x1b[B' ,b'\x1b[B' ,b'\x1b[1;2B',b'\x1b[1;6B',b'\x1b[1;6B'],
	Qt.Key.Key_Right     : [b'\x1b[C' ,b'\x1b[1;2C',b'\x1b[1;5C',b'\x1b\x1b[C' ,b'\x1b[C' ,b'\x1b[1;2C',b'\x1b[1;6C',b'\x1b[1;6C'],
	Qt.Key.Key_Left      : [b'\x1b[D' ,b'\x1b[1;2D',b'\x1b[1;5D',b'\x1b\x1b[D' ,b'\x1b[D' ,b'\x1b[1;2D',b'\x1b[1;6D',b'\x1b[1;6D'],
	Qt.Key.Key_Home      : [b'\x1b[H' ,b'\x1b[1;2H',b'\x1b[1;5H',b'\x1b[1;9H'  ,b'\x1b[H' ,b'\x1b[1;2H',b'\x1b[1;6H',b'\x1b[1;6H'],
	Qt.Key.Key_End       : [b'\x1b[F' ,b'\x1b[1;2F',b'\x1b[1;5F',b'\x1b[1;9F'  ,b'\x1b[F' ,b'\x1b[1;2F',b'\x1b[1;6F',b'\x1b[1;6F'],
	Qt.Key.Key_PageUp    : [b'\x1b[5~',b"\x1b[1;4A",b'\x1b[5~'  ,b'\x1b\x1b[5~',b'\x1b[5~',b'\x1b[5~'  ,b'\x1b[5~'  ,b'\x1b[5~'  ],
	Qt.Key.Key_PageDown  : [b'\x1b[6~',b"\x1b[1;4B",b'\x1b[6~'  ,b'\x1b\x1b[6~',b'\x1b[6~',b'\x1b[6~'  ,b'\x1b[6~'  ,b'\x1b[6~'  ],
}

def convert_key_to_vt100(key_event):
	""" Convert the key event qt into vt100 key """
	result = None
	key = key_event.key()
	try:
		# PyQt6
		modifier = key_event.keyCombination().keyboardModifiers() & ~Qt.KeyboardModifier.KeypadModifier
	except:
		# PyQt5
		modifier = key_event.modifiers()& ~Qt.KeyboardModifier.KeypadModifier

	if key >= 0x1000000:
		# Manage main keys
		if key in main_keys:
			result = main_keys[key]
		# Manage function keys
		elif key in function_keys:
			normal, shift = function_keys[key]
			if modifier & Qt.KeyboardModifier.ShiftModifier:
				result = shift
			else:
				result = normal
		# Manage move keys
		elif key in move_keys:
			normal, shift, meta, alt, control, shift_alt, shift_meta, shift_control = move_keys[key]
			if modifier & Qt.KeyboardModifier.ShiftModifier and modifier & Qt.KeyboardModifier.MetaModifier:
				result = shift_meta
			elif modifier & Qt.KeyboardModifier.ShiftModifier and modifier & Qt.KeyboardModifier.AltModifier:
				result = shift_alt
			elif modifier & Qt.KeyboardModifier.ShiftModifier and modifier & Qt.KeyboardModifier.ControlModifier:
				result = shift_control
			elif modifier & Qt.KeyboardModifier.ShiftModifier:
				result = shift
			elif modifier & Qt.KeyboardModifier.MetaModifier:
				result = meta
			elif modifier & Qt.KeyboardModifier.AltModifier:
				result = alt
			elif modifier & Qt.KeyboardModifier.ControlModifier:
				result = control
			else:
				result = normal
	else:
		result = key_event.text().encode("utf-8")
	return result

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

	def accept(self):
		self.close()
class FlashDialog(QDialog):
	""" Dialog box to select firmware """
	def __init__(self, parent):
		""" Dialog box constructor """
		QDialog.__init__(self, parent)
		try:
			self.dialog = uic.loadUi('dialogflash.ui', self)
		except Exception as err:
			from dialogflash import Ui_dialog_flash
			self.dialog = Ui_dialog_flash()
			self.dialog.setupUi(self)

		self.dialog.select_firmware.clicked.connect(self.on_firmware_clicked)
		self.dialog.baud.addItems(["9600","57600","74880","115200","230400","460800"])
		self.dialog.baud.setCurrentIndex(5)

	def accept(self):
		""" Called when ok pressed """
		if os.path.exists(self.dialog.firmware.text()) is False:
			msg = QMessageBox()
			w = self.geometry().width()
			h = self.geometry().height()
			x = self.geometry().x()
			y = self.geometry().y()
			msg.setGeometry(x + w//3,y + h//3,w,h)
			msg.setIcon(QMessageBox.Icon.Critical)
			msg.setText("Firmware not found")
			msg.exec()
		else:
			super().accept()

	def on_firmware_clicked(self, event):
		""" Selection of firmware button clicked """
		firmware = QFileDialog.getOpenFileName(self, 'Select firmware file', '',"Firmware files (*.bin)")
		if firmware != ('', ''):
			self.dialog.firmware.setText(firmware[0])

class CamFlasher(QMainWindow):
	""" Tools to flash the firmware of pycameresp """
	def __init__(self):
		""" Main window contructor """
		super(CamFlasher, self).__init__()
		try:
			self.window = uic.loadUi('camflasher.ui', self)
		except Exception as err:
			from camflasher import Ui_main_window
			self.window = Ui_main_window()
			self.window.setupUi(self)

		self.window.output.installEventFilter(self)

		self.flash_dialog = FlashDialog(self)
		self.about_dialog = AboutDialog(self)

		# Start stdout redirection vt100 console
		self.window.output.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.window.output.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.console = QStdoutVT100(self.window.output)

		# Serial listener thread
		self.flasher = Flasher()
		self.flasher.start()

		# Refresher of the console content
		self.timer_refresh_console = QTimer(active=True, interval=100)
		self.timer_refresh_console.timeout.connect(self.on_refresh_console)
		self.timer_refresh_console.start()

		# Refresher of the list of serial port available
		self.timer_refresh_port = QTimer(active=True, interval=500)
		self.timer_refresh_port.timeout.connect(self.on_refresh_port)
		self.timer_refresh_port.start()
		self.serial_ports = []

		self.port_selected = None
		self.window.combo_port.currentTextChanged.connect(self.on_port_changed)

		self.move(10,200)
		self.show()
		self.resize_console()
		self.paused = False
		self.window.output.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
		self.window.output.customContextMenuRequested.connect(self.context_menu)

		self.window.action_paste.triggered.connect(self.paste)
		self.window.action_copy.triggered.connect(self.copy)
		self.window.action_pause.triggered.connect(self.pause)
		self.window.action_resume.triggered.connect(self.pause)
		self.window.action_resume.setDisabled(True)
		self.window.action_flash.triggered.connect(self.on_flash_clicked)
		self.window.action_about.triggered.connect(self.on_about_clicked)

	def on_about_clicked(self):
		""" About menu clicked """
		self.about_dialog.show()
		self.about_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
		self.about_dialog.exec()

	def context_menu(self, pos):
		""" Customization of the context menu """
		context = QMenu(self)

		copy = QAction("Copy", self)
		copy.triggered.connect(self.copy)
		context.addAction(copy)

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
		self.console.stdout.write("Paste '%s'\n"%QApplication.clipboard().text())

	def eventFilter(self, obj, event):
		""" Treat key pressed on console """
		if event.type() == QEvent.Type.KeyPress:
			key = convert_key_to_vt100(event)
			if key is not None:
				if self.paused is False:
					self.flasher.send_key(key)
			return True
		return super(CamFlasher, self).eventFilter(obj, event)

	def get_size(self):
		""" Get the size of VT100 console """
		# Calculate the dimension in pixels of a text of 200 lines with 200 characters
		line = "W"*200 + "\n"
		line = line*200
		line = line[:-1]
		size = self.window.output.fontMetrics().size(Qt.TextFlag.TextWordWrap,line)

		# Deduce the size of console visible in the window
		width  = (self.window.output.contentsRect().width()  * 200)// size.width() -  1
		height = (self.window.output.contentsRect().height() * 200)// size.height()
		return width, height

	def resize_console(self):
		""" Resize console """
		# Calculate the dimension in pixels of a text of 200 lines with 200 characters
		line = "W"*200 + "\n"
		line = line*200
		line = line[:-1]
		size = self.window.output.fontMetrics().size(Qt.TextFlag.TextWordWrap,line)

		# Deduce the size of console visible in the window
		width  = (self.window.output.contentsRect().width()  * 200)// size.width() -  1
		height = (self.window.output.contentsRect().height() * 200)// size.height()
		self.console.set_size(width, height)

	def resizeEvent(self, _):
		""" Treat the window resize event """
		self.resize_console()

	def on_refresh_port(self):
		""" Refresh the combobox content with the serial ports detected """
		# self.console.test()
		ports = []
		for port, _, _ in sorted(list_ports.comports()):
			if not "Bluetooth" in port and not "Wireless" in port:
				ports.append(port)

		# If the list of serial port changed
		if self.serial_ports != ports:
			self.serial_ports = ports

			for i in range(self.window.combo_port.count()):
				if not self.window.combo_port.itemText(i) in ports:
					self.window.combo_port.removeItem(i)

			for port in ports:
				for i in range(self.window.combo_port.count()):
					if self.window.combo_port.itemText(i) == port:
						break
				else:
					self.window.combo_port.addItem(port)

	def on_port_changed(self, event):
		""" On port changed event """
		self.flasher.set_info(port = self.get_port())

	def on_firmware_clicked(self, event):
		""" Selection of firmware button clicked """
		firmware = QFileDialog.getOpenFileName(self, 'Select firmware file', '',"Firmware files (*.bin)")
		if firmware != ('', ''):
			self.window.txt_firmware.setText(firmware[0])

	def on_flash_clicked(self, event):
		""" Flash of firmware button clicked """
		self.flash_dialog.show()
		self.flash_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
		result = self.flash_dialog.exec()
		if result == 1 and self.window.combo_port.currentText() != "":
			try:
				firmware  = self.flash_dialog.dialog.firmware.text()
				baud      = self.flash_dialog.dialog.baud.currentText()
				erase     = self.flash_dialog.dialog.erase.isChecked()
				port      = self.window.combo_port.currentText()
				self.flasher.flash(port, baud, firmware, erase)
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
		self.window.output.viewport().setProperty("cursor", QCursor(Qt.CursorShape.ArrowCursor))
		if self.paused is False:
			output = self.console.refresh()
			if output != "":
				self.flasher.send_key(output.encode("utf-8"))

	def closeEvent(self, event):
		""" On close window event """
		# Terminate stdout redirection
		self.console.close()

		# Stop serial thread
		self.flasher.quit()

def main():
	""" Main application """
	app = QApplication(sys.argv)
	window = CamFlasher()
	app.exec()

if __name__ == "__main__":
	main()
