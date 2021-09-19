# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Simulation ESP32CAM camera class, used on desktop to debug with vscode """
_current = 0
_opened = False
_pixformat     = 0
_aec_value     = 0
_framesize     = 0
_quality       = 0
_special_effect= 0
_wb_mode       = 0
_agc_gain      = 0
_gainceiling   = 0
_brightness    = 0
_contrast      = 0
_saturation    = 0
_sharpness     = 0
_ae_level      = 0
_denoise       = 0
_whitebal      = 0
_awb_gain      = 0
_exposure_ctrl = 0
_aec2          = 0
_gain_ctrl     = 0
_bpc           = 0
_wpc           = 0
_raw_gma       = 0
_lenc          = 0
_hmirror       = 0
_vflip         = 0
_dcw           = 0
_colorbar      = 0
FRAMESIZE_96X96     = 0
FRAMESIZE_QQVGA     = 0
FRAMESIZE_QCIF      = 0
FRAMESIZE_HQVGA     = 0
FRAMESIZE_240X240   = 0
FRAMESIZE_QVGA      = 0
FRAMESIZE_CIF       = 0
FRAMESIZE_HVGA      = 0
FRAMESIZE_VGA       = 0
FRAMESIZE_SVGA      = 0
FRAMESIZE_XGA       = 0
FRAMESIZE_HD        = 0
FRAMESIZE_SXGA      = 0
FRAMESIZE_UXGA      = 0
FRAMESIZE_FHD       = 0
FRAMESIZE_P_HD      = 0
FRAMESIZE_P_3MP     = 0
FRAMESIZE_QXGA      = 0
FRAMESIZE_QHD       = 0
FRAMESIZE_WQXGA     = 0
FRAMESIZE_P_FHD     = 0
FRAMESIZE_QSXGA     = 0

PIXFORMAT_RGB565    = 0
PIXFORMAT_YUV422    = 0
PIXFORMAT_GRAYSCALE = 0
PIXFORMAT_JPEG      = 0
PIXFORMAT_RGB888    = 0
PIXFORMAT_RAW       = 0
PIXFORMAT_RGB444    = 0
PIXFORMAT_RGB555    = 0

def init():
	global _opened
	if _opened == False:
		_opened = True
		return True
	return False

def deinit():
	global _opened
	if _opened == True:
		_opened = False
		return True
	return False

def capture():
	global _opened
	global _current
	if _opened:
		if _current == 0:
			data = open("Test2.jpg","rb").read()
			_current = 1
		else:
			data = open("Test1.jpg","rb").read()
			_current = 0
		return data
	return None

class Motion:
	sizeBase = [10*1024]
	sizeDirection = [1]
	""" Class motion detection returned by the detect function """
	def __init__(self, motion_):
		self.size = self.sizeBase[0]
		if self.sizeDirection[0] == 1:
			self.sizeBase[0] += 1024
			if self.sizeBase[0] > 66*1024:
				self.sizeDirection[0] = 0
		else:
			self.sizeBase[0] -= 1024
			if self.sizeBase[0] < 10*1024:
				self.sizeDirection[0] = 1

	def deinit (self):
		pass

	def setMask(self):
		pass

	def compare(self, other, extractShape):
		return {
			'feature': {'light': 37, 'saturation': 13}, 
			'path': '2021-04-25 11-37-00', 
			'diff': {'squarex': 40, 'squarey': 40, 'width': 20, 'height': 15, 'max': 300, 'count': 0, 'light': 94, 'errhisto':256, 'diffhisto':256}, 
			'shapes': 
			[
				{'size': 35, 'id': 1, 'height': 360, 'width': 200, 'y': 0, 'x': 0, 'centerx': 40, 'centery': 120},
				{'size': 94, 'id': 2, 'height': 600, 'width': 400, 'y': 0, 'x': 360, 'centerx': 480, 'centery': 240}
			], 
			'index': 5417, 
			'image': '21-04-25 11-37-01 Id=5417 D=129.jpg', 
			'date': '2021-04-25 11-37-01', 
			'motionId': 46, 
			'geometry': {'height': 600, 'width': 800}
		}

	def configure(self, config):
		pass

	def getImage(self):
		return b""

	def getSize(self):
		return self.size

	def getLight(self):
		return 128

def motion():
	return Motion(None)

def pixformat(val=None):
	global _pixformat
	if val != None:
		_pixformat = val
	return _pixformat

def aec_value     (val=None):
	global _aec_value
	if val != None:
		_aec_value = val
	return _aec_value

def framesize     (val=None):
	global _framesize
	if val != None:
		_framesize = val
	return _framesize

def quality       (val=None):
	global _quality
	if val != None:
		_quality = val
	return _quality

def special_effect(val=None): 
	global _special_effect
	if val != None:
		_special_effect = val
	return _special_effect

def wb_mode       (val=None):
	global _wb_mode
	if val != None:
		_wb_mode = val
	return _wb_mode

def agc_gain      (val=None):
	global _agc_gain
	if val != None:
		_agc_gain = val
	return _agc_gain

def gainceiling   (val=None):
	global _gainceiling
	if val != None:
		_gainceiling = val
	return _gainceiling

def brightness    (val=None):
	global _brightness
	if val != None:
		_brightness = val
	return _brightness

def contrast      (val=None): 
	global _contrast
	if val != None:
		_contrast  = val
	return _contrast 

def saturation    (val=None):
	global _saturation
	if val != None:
		_saturation = val
	return _saturation

def sharpness     (val=None):
	global _sharpness
	if val != None:
		_sharpness = val
	return _sharpness

def ae_level      (val=None):
	global _ae_level
	if val != None:
		_ae_level = val
	return _ae_level

def denoise       (val=None):
	global _denoise
	if val != None:
		_denoise = val
	return _denoise

def whitebal      (val=None):
	global _whitebal
	if val != None:
		_whitebal = val
	return _whitebal

def awb_gain      (val=None):
	global _awb_gain
	if val != None:
		_awb_gain = val
	return _awb_gain

def exposure_ctrl (val=None):
	global _exposure_ctrl
	if val != None:
		_exposure_ctrl = val
	return _exposure_ctrl

def aec2          (val=None):
	global _aec2
	if val != None:
		_aec2 = val
	return _aec2

def gain_ctrl     (val=None):
	global _gain_ctrl
	if val != None:
		_gain_ctrl = val
	return _gain_ctrl

def bpc           (val=None):
	global _bpc
	if val != None:
		_bpc = val
	return _bpc

def wpc           (val=None):
	global _wpc
	if val != None:
		_wpc = val
	return _wpc

def raw_gma       (val=None):
	global _raw_gma
	if val != None:
		_raw_gma = val
	return _raw_gma

def lenc          (val=None):
	global _lenc
	if val != None:
		_lenc = val
	return _lenc

def hmirror       (val=None):
	global _hmirror
	if val != None:
		_hmirror = val
	return _hmirror

def vflip         (val=None):
	global _vflip
	if val != None:
		_vflip = val
	return _vflip

def dcw           (val=None):
	global _dcw
	if val != None:
		_dcw = val
	return _dcw

def colorbar      (val=None):
	global _colorbar
	if val != None:
		_colorbar = val
	return _colorbar

def isavailable():
	return True

def flash(level):
	pass