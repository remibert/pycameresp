""" Tools to flash the firmware of pycameresp """
import sys
# pylint:disable=no-name-in-module
from PyQt6 import uic
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QApplication
from serial.tools import list_ports
from flasher import Flasher
from qstdoutvt100 import QStdoutVT100

class CamFlasher(QMainWindow):
	""" Tools to flash the firmware of pycameresp """
	def __init__(self):
		""" Main window contructor """
		super(CamFlasher, self).__init__()
		try:
			self.ui = uic.loadUi('camflasher.ui', self)
		except:
			from camflasher import Ui_MainWindow
			self.ui = Ui_MainWindow()
			self.ui.setupUi(self)


		# Console vt100
		self.stdout = sys.stdout
		self.console = QStdoutVT100(self.ui.txt_result)
		sys.stdout = self.console

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
		self.i = 0
		# print("\x1B[93;101mCannot open serial port")
		# print("tii\x1B[2KToto")
		self.show()

	def on_refresh_port(self):
		""" Refresh the combobox content with the serial ports detected """
		ports = []
		for port, desc, hwid in sorted(list_ports.comports()):
			if not "Bluetooth" in port and not "Wireless" in port:
				ports.append(port)

		# If the list of serial port changed
		if self.serial_ports != ports:
			self.serial_ports = ports
			self.ui.cbo_port.clear()
			self.ui.cbo_port.addItems(ports)
			self.flasher.set_info(port=self.get_port())

	def on_firmware_clicked(self, event):
		""" Selection of firmware button clicked """
		firmware = QFileDialog.getOpenFileName(self, 'Select firmware file', '',"Firmware files (*.bin)")
		if firmware != ('', ''):
			self.ui.txt_firmware.setText(firmware[0])

	def on_flash_clicked(self, event):
		""" Flash of firmware button clicked """
		port     = self.ui.cbo_port.currentText()
		firmware = self.ui.txt_firmware.text()
		erase    = self.ui.chk_erase.isChecked()
		self.flasher.set_info(port, firmware, erase)

	def get_port(self):
		""" Get the name of serial port """
		try:
			result = self.ui.cbo_port.currentText()
		except:
			result = None
		return result

	def on_refresh_console(self):
		""" Refresh the console content """
		self.console.refresh()
		# string = ""
		# for i in range(1000):
		# 	string += chr(0x21 + self.i)
		# self.i += 1
		# if self.i + 0x21 >= 0x7F:
		# 	self.i = 0
		# print(string)

	def closeEvent(self, event):
		""" On close window event """
		# Stop serial thread
		self.flasher.cancel()

def main():
	""" Main application """
	app = QApplication(sys.argv)
	window = CamFlasher()
	app.exec()

if __name__ == "__main__":
	main()
	