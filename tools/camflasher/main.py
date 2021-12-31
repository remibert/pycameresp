""" Tools to flash the firmware of pycameresp """
import sys
# pylint:disable=no-name-in-module
import os.path
from PyQt6 import uic
from PyQt6.QtCore import QTimer, QEvent, Qt
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QApplication, QMessageBox
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
	modifier = key_event.keyCombination().keyboardModifiers() & ~Qt.KeyboardModifier.KeypadModifier

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

class CamFlasher(QMainWindow):
	""" Tools to flash the firmware of pycameresp """
	def __init__(self):
		""" Main window contructor """
		super(CamFlasher, self).__init__()
		try:
			self.ui = uic.loadUi('camflasher.ui', self)
		except:
			from camflasher import Ui_win_main
			self.ui = Ui_win_main()
			self.ui.setupUi(self)
		
		self.ui.txt_result.installEventFilter(self)

		# Start stdout redirection vt100 console
		self.ui.txt_result.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.ui.txt_result.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.console = QStdoutVT100(self.ui.txt_result)

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

		self.ui.but_firmware.clicked.connect(self.on_firmware_clicked)
		self.ui.but_flash.clicked.connect(self.on_flash_clicked)
		self.ui.cbo_baud.addItems(["9600","57600","74880","115200","230400","460800"])
		self.ui.cbo_baud.setCurrentIndex(5)

		self.port_selected = None
		self.ui.cbo_port.currentTextChanged.connect(self.on_port_changed)

		#~ self.move(0,0)
		self.show()
		self.console.resizeEvent()

	def eventFilter(self, obj, event):
		""" Treat key pressed on console """
		if event.type() == QEvent.Type.KeyPress:
			key = convert_key_to_vt100(event)
			if key is not None:
				self.flasher.send_key(key)
			return True
		return super(CamFlasher, self).eventFilter(obj, event)

	def resizeEvent(self, _):
		""" Treat the window resize event """
		self.console.resizeEvent()

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

			for i in range(self.ui.cbo_port.count()):
				if not self.ui.cbo_port.itemText(i) in ports:
					self.ui.cbo_port.removeItem(i)

			for port in ports:
				for i in range(self.ui.cbo_port.count()):
					if self.ui.cbo_port.itemText(i) == port:
						break
				else:
					self.ui.cbo_port.addItem(port)

	def on_port_changed(self, event):
		""" On port changed event """
		self.flasher.set_info(port = self.get_port())

	def on_firmware_clicked(self, event):
		""" Selection of firmware button clicked """
		firmware = QFileDialog.getOpenFileName(self, 'Select firmware file', '',"Firmware files (*.bin)")
		if firmware != ('', ''):
			self.ui.txt_firmware.setText(firmware[0])

	def on_flash_clicked(self, event):
		""" Flash of firmware button clicked """
		port     = self.ui.cbo_port.currentText()
		baud     = self.ui.cbo_baud.currentText()
		firmware = self.ui.txt_firmware.text()
		erase    = self.ui.chk_erase.isChecked()
		if os.path.exists(firmware) is False:
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
			self.flasher.flash(port, baud, firmware, erase)

	def get_port(self):
		""" Get the name of serial port """
		try:
			result = self.ui.cbo_port.currentText()
		except:
			result = None
		return result

	def on_refresh_console(self):
		""" Refresh the console content """
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
