""" Tools to flash the firmware of pycameresp """
# pylint:disable=no-name-in-module
import copy
import sys
import os.path
import os
from pathlib import Path
from platform import uname

sys.path.append("../../modules/lib/tools")
# pylint:disable=import-error
# pylint:disable=wrong-import-position

try:
	from PyQt6 import uic
	from PyQt6.QtCore import QSettings
	from PyQt6.QtWidgets import QFileDialog, QColorDialog, QDialog, QMessageBox
	from PyQt6.QtGui import QFont,QColor
except:
	from PyQt5 import uic
	from PyQt5.QtCore import QSettings
	from PyQt5.QtWidgets import QFileDialog, QColorDialog, QDialog, QMessageBox
	from PyQt5.QtGui import QFont,QColor

# Settings
SETTINGS_FILENAME  = "CamFlasher.ini"
FONT_FAMILY        = "camflasher.font.family"
FONT_SIZE          = "camflasher.font.size"
WORKING_DIRECTORY  = "camflasher.working_directory"
WIN_GEOMETRY       = "camflasher.window.geometry"
FIRMWARE_FILENAMES = "camflasher.firmware.filenames"
TELNET_HOSTS       = "camflasher.telnet.host"
DEVICE_RTS_DTR     = "camflasher.device.rts_dtr"
FIELD_COLORS       = "camflasher.colors"
TYPE_LINK          = "camflasher.link.type"

# DEFAULT_TEXT_BACKCOLOR    = 0xFFFAE6
# DEFAULT_TEXT_FORECOLOR    = 0x4D4700
# DEFAULT_CURSOR_BACKCOLOR  = 0x645D00
# DEFAULT_CURSOR_FORECOLOR  = 0xFFFCD9
# DEFAULT_REVERSE_BACKCOLOR = 0xDFD9A8
# DEFAULT_REVERSE_FORECOLOR = 0x322D00

DEFAULT_COLORS = {
	"text_colors":{
		"text_backcolor"   : 0xFFFAE6,
		"text_forecolor"   : 0x4D4700,
		"cursor_backcolor" : 0x645D00,
		"cursor_forecolor" : 0xFFFCD9,
		"reverse_backcolor": 0xDFD9A8,
		"reverse_forecolor": 0x322D00,
	},
	"ansi_colors":[
		0x000000, 0xAA0000, 0x00AA00, 0xAA5500, 0x0000AA, 0xAA00AA, 0x00AAAA, 0xAAAAAA,
		0x555555, 0xFF5555, 0x55FF55, 0xFFFF55, 0x5555FF, 0xFF55FF, 0x55FFFF, 0xFFFFFF]
}

DOWNLOAD_VERSION = "Download the lastest version of :"

OUTPUT_TEXT = """
<html>
	<head/>
		<body style="background-color: %(text_backcolor)s">
			<p style="font-size: 2em;color : %(text_forecolor)s" >	
				<span style="color:%(comment_color)s;">#&nbsp;Comment</span><br>
				<span style="font-weight: bold;color:%(keyword_color)s">class</span><span style="font-weight: bold;color:%(class_color)s;">&nbsp;Class</span><span >:</span><br>
				<span >&nbsp;&nbsp;&nbsp;</span><span style="font-weight: bold;color:%(keyword_color)s">def</span><span style="font-weight: bold;color:%(function_color)s">&nbsp;function</span><span >(</span><span style="font-weight: bold;color:%(keyword_color)s">self</span><span >):</span><br>
				<span >&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;integer&nbsp;=&nbsp;</span><span style="color:%(number_color)s">12345</span><br>
				<span >&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;string&nbsp;=&nbsp;</span><span style="color:%(string_color)s">&quot;Hello&quot;</span><br>
				<span >&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;v&nbsp;=&nbsp;</span><span style="background-color : %(reverse_backcolor)s;color : %(reverse_forecolor)s">&quot;Reverse&quot;&nbsp;</span><span style="background-color : %(cursor_backcolor)s;color : %(cursor_forecolor)s">#</span><br><br><br>
			</p>
	</body>
</html>"""

# DEFAULT_COMMENT_COLOR  = 0x00AA00
# DEFAULT_KEYWORD_COLOR  = 0x0000AA
# DEFAULT_CLASS_COLOR    = 0xAA00AA
# DEFAULT_FUNCTION_COLOR = 0x00AAAA
# DEFAULT_NUMBER_COLOR   = 0xAA5500
# DEFAULT_STRING_COLOR   = 0xAA0000

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

		self.colors = settings.value(FIELD_COLORS, copy.deepcopy(DEFAULT_COLORS))
		settings.setValue(FIELD_COLORS,copy.deepcopy(DEFAULT_COLORS))
		self.dialog.select_directory.clicked.connect(self.on_directory_clicked)
		self.dialog.button_forecolor.clicked.connect(self.on_forecolor_clicked)
		self.dialog.button_backcolor.clicked.connect(self.on_backcolor_clicked)
		self.dialog.button_cursor_forecolor.clicked.connect(self.on_cursor_forecolor_clicked)
		self.dialog.button_cursor_backcolor.clicked.connect(self.on_cursor_backcolor_clicked)
		self.dialog.button_reverse_forecolor.clicked.connect(self.on_reverse_forecolor_clicked)
		self.dialog.button_reverse_backcolor.clicked.connect(self.on_reverse_backcolor_clicked)

		for i in range(16):
			eval('self.dialog.color_%d.clicked.connect (self.on_ansi_color_%d_clicked)'%(i,i))
	
		self.refresh_palette()

		self.dialog.reset_color.clicked.connect(self.on_reset_color_clicked)
		self.dialog.reset_palette.clicked.connect(self.on_reset_palette_clicked)
		self.dialog.combo_font.currentTextChanged.connect(self.on_font_changed)
		self.dialog.spin_font_size.valueChanged.connect(self.on_font_changed)
		self.refresh_output()
		self.setModal(True)

	def refresh_palette(self):
		""" Refresh the ansi palette """
		for i in range(16):
			backcolor = '%06X'%self.colors["ansi_colors"][i]
			forecolor = '%06X'%(self.colors["ansi_colors"][i]^0xFFFFFF)
			eval('self.dialog.color_%d.setStyleSheet ("color:#%s;background-color: #%s")'%(i,forecolor,backcolor))

	def int_to_rgb(self, color):
		""" Convert integer to rgb color """
		r = (color & 0xFF0000) >> 16
		g = (color & 0x00FF00) >> 8
		b = (color & 0x0000FF)
		return "rgb(%d,%d,%d)"%(r,g,b)

	def qcolor_to_int(self, color):
		r,g,b,a = color.getRgb()
		return  r << 16 | g << 8 | b

	def int_to_qcolor(self, color):
		r = (color & 0xFF0000) >> 16
		g = (color & 0x00FF00) >> 8
		b = (color & 0x0000FF)
		return QColor(r,g,b)

	def refresh_output(self):
		""" Refresh the output """
		font = QFont()
		font.setFamily    (self.dialog.combo_font.currentFont().family())
		font.setPointSize (int(self.dialog.spin_font_size.value()))
		self.dialog.label_output.setFont(font)

		# pylint:disable=possibly-unused-variable
		text_backcolor     = self.int_to_rgb(self.colors["text_colors"]["text_backcolor"])
		text_forecolor     = self.int_to_rgb(self.colors["text_colors"]["text_forecolor"])
		cursor_backcolor   = self.int_to_rgb(self.colors["text_colors"]["cursor_backcolor"])
		cursor_forecolor   = self.int_to_rgb(self.colors["text_colors"]["cursor_forecolor"])
		reverse_backcolor  = self.int_to_rgb(self.colors["text_colors"]["reverse_backcolor"])
		reverse_forecolor  = self.int_to_rgb(self.colors["text_colors"]["reverse_forecolor"])
		comment_color      = self.int_to_rgb(self.colors["ansi_colors"][2])
		keyword_color      = self.int_to_rgb(self.colors["ansi_colors"][4])
		class_color        = self.int_to_rgb(self.colors["ansi_colors"][5])
		function_color     = self.int_to_rgb(self.colors["ansi_colors"][6])
		number_color       = self.int_to_rgb(self.colors["ansi_colors"][3])
		string_color       = self.int_to_rgb(self.colors["ansi_colors"][1])

		self.dialog.label_output.setHtml(OUTPUT_TEXT%locals())

	def on_directory_clicked(self, event):
		""" Selection of directory button clicked """
		settings = get_settings()
		directory = QFileDialog.getExistingDirectory(self, 'Select working directory', directory =settings.value(WORKING_DIRECTORY,str(Path.home())))
		if directory != '':
			self.dialog.working_directory.setText(directory)

	def on_reset_color_clicked(self):
		""" Reset the default color """
		self.colors["text_colors"]    = copy.deepcopy(DEFAULT_COLORS["text_colors"])
		self.refresh_output()

	def on_reset_palette_clicked(self):
		""" Reset the default ansi color """
		self.colors["ansi_colors"]    = copy.deepcopy(DEFAULT_COLORS["ansi_colors"])
		self.refresh_palette()
		self.refresh_output()

	def on_font_changed(self, event):
		""" Font family changed """
		self.refresh_output()

	# pylint:disable=missing-docstring
	# pylint:disable=multiple-statements
	def on_ansi_color_0_clicked (self, event):self.on_ansi_color_clicked(0)
	def on_ansi_color_1_clicked (self, event):self.on_ansi_color_clicked(1)
	def on_ansi_color_2_clicked (self, event):self.on_ansi_color_clicked(2)
	def on_ansi_color_3_clicked (self, event):self.on_ansi_color_clicked(3)
	def on_ansi_color_4_clicked (self, event):self.on_ansi_color_clicked(4)
	def on_ansi_color_5_clicked (self, event):self.on_ansi_color_clicked(5)
	def on_ansi_color_6_clicked (self, event):self.on_ansi_color_clicked(6)
	def on_ansi_color_7_clicked (self, event):self.on_ansi_color_clicked(7)
	def on_ansi_color_8_clicked (self, event):self.on_ansi_color_clicked(8)
	def on_ansi_color_9_clicked (self, event):self.on_ansi_color_clicked(9)
	def on_ansi_color_10_clicked(self, event):self.on_ansi_color_clicked(10)
	def on_ansi_color_11_clicked(self, event):self.on_ansi_color_clicked(11)
	def on_ansi_color_12_clicked(self, event):self.on_ansi_color_clicked(12)
	def on_ansi_color_13_clicked(self, event):self.on_ansi_color_clicked(13)
	def on_ansi_color_14_clicked(self, event):self.on_ansi_color_clicked(14)
	def on_ansi_color_15_clicked(self, event):self.on_ansi_color_clicked(15)
	# pylint:enable=missing-docstring
	# pylint:enable=multiple-statements

	def on_ansi_color_clicked(self, ident):
		""" Choose ansi color """
		color = eval("self.dialog.color_%d.styleSheet()"%ident)
		color = color.split("#")[2]
		color = QColor(eval("0x%s"%color[0:2]), eval("0x%s"%color[2:4]), eval("0x%s"%color[4:6]))
		color = QColorDialog.getColor(parent=self, initial=color, title="Ansi color")
		if color.isValid():
			self.colors["ansi_colors"][ident] = self.qcolor_to_int(color)
			self.refresh_palette()
			self.refresh_output()

	def on_forecolor_clicked(self, event):
		""" Select the forecolor """
		color = QColorDialog.getColor(parent=self, initial=self.int_to_qcolor(self.colors["text_colors"]["text_forecolor"]), title="Text color")
		if color.isValid():
			self.colors["text_colors"]["text_forecolor"] = self.qcolor_to_int(color)
			self.refresh_output()

	def on_backcolor_clicked(self, event):
		""" Select the backcolor """
		color = QColorDialog.getColor(parent=self, initial=self.int_to_qcolor(self.colors["text_colors"]["text_backcolor"]), title="Background color")
		if color.isValid():
			self.colors["text_colors"]["text_backcolor"] = self.qcolor_to_int(color)
			self.refresh_output()

	def on_cursor_forecolor_clicked(self, event):
		""" Select the cursor forecolor """
		color = QColorDialog.getColor(parent=self, initial=self.int_to_qcolor(self.colors["text_colors"]["cursor_forecolor"]), title="Cursor text color")
		if color.isValid():
			self.colors["text_colors"]["cursor_forecolor"] = self.qcolor_to_int(color)
			self.refresh_output()

	def on_cursor_backcolor_clicked(self, event):
		""" Select the cursor backcolor """
		color = QColorDialog.getColor(parent=self, initial=self.int_to_qcolor(self.colors["text_colors"]["cursor_backcolor"]), title="Cursor background color")
		if color.isValid():
			self.colors["text_colors"]["cursor_backcolor"] = self.qcolor_to_int(color)
			self.refresh_output()

	def on_reverse_forecolor_clicked(self, event):
		""" Select the reverse forecolor """
		color = QColorDialog.getColor(parent=self, initial=self.int_to_qcolor(self.colors["text_colors"]["reverse_forecolor"]), title="Reverse text color")
		if color.isValid():
			self.colors["text_colors"]["reverse_forecolor"] = self.qcolor_to_int(color)
			self.refresh_output()

	def on_reverse_backcolor_clicked(self, event):
		""" Select the reverse backcolor """
		color = QColorDialog.getColor(parent=self, initial=self.int_to_qcolor(self.colors["text_colors"]["reverse_backcolor"]), title="Reverse background color")
		if color.isValid():
			self.colors["text_colors"]["reverse_backcolor"] = self.qcolor_to_int(color)
			self.refresh_output()

	def accept(self):
		""" Accept about dialog """
		font = self.dialog.combo_font.currentFont()
		settings = get_settings()
		settings.setValue(FONT_FAMILY , font.family())
		settings.setValue(FONT_SIZE   , self.dialog.spin_font_size.value())
		settings.setValue(WORKING_DIRECTORY, self.dialog.working_directory.text())
		settings.setValue(FIELD_COLORS, self.colors)
		super().accept()
