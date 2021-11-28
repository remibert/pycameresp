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
	""" Initialize camera """
	global _opened
	if _opened is False:
		_opened = True
		return True
	return False

def deinit():
	""" Stop camera """
	global _opened
	if _opened is True:
		_opened = False
		return True
	return False

def capture():
	""" Capture image """
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
	""" Class motion detection returned by the detect function """
	size_base = [10*1024]
	size_direction = [1]
	def __init__(self, motion_):
		""" Constructor of motion """
		self.size = self.size_base[0]
		if self.size_direction[0] == 1:
			self.size_base[0] += 1024
			if self.size_base[0] > 66*1024:
				self.size_direction[0] = 0
		else:
			self.size_base[0] -= 1024
			if self.size_base[0] < 10*1024:
				self.size_direction[0] = 1

	def deinit (self):
		""" Deinit motion """

	def compare(self, other):
		""" Compare two motion detection """
		return {
			'feature': {'light': 37, 'saturation': 13},
			'path': '2021-04-25 11-37-00',
			'diff': {'squarex': 40, 'squarey': 40, 'width': 20, 'height': 15, 'max': 300, 'count': 0, 'light': 94, 'errhisto':256, 'diffhisto':256},
			'index': 5417,
			'image': '21-04-25 11-37-01 Id=5417 D=129.jpg',
			'date': '2021-04-25 11-37-01',
			'motion_id': 46,
			'geometry': {'height': 600, 'width': 800}
		}

	def configure(self, config):
		""" Configure motion detection """

	def get_image(self):
		""" Get the image from motion """
		return b""

	def get_size(self):
		""" Get the size of image """
		return self.size

	def get_light(self):
		""" Get light level """
		return 128

def motion():
	""" Get motion detection """
	return Motion(None)

def pixformat(val=None):
	""" Set or get pixformat """
	global _pixformat
	if val is not None:
		_pixformat = val
	return _pixformat

def aec_value     (val=None):
	""" Set or get automatic exposure control value """
	global _aec_value
	if val is not None:
		_aec_value = val
	return _aec_value

def framesize     (val=None):
	""" Set or get framesize """
	global _framesize
	if val is not None:
		_framesize = val
	return _framesize

def quality       (val=None):
	""" Set or get image quality compression """
	global _quality
	if val is not None:
		_quality = val
	return _quality

def special_effect(val=None):
	""" Set or get special effect """
	global _special_effect
	if val is not None:
		_special_effect = val
	return _special_effect

def wb_mode       (val=None):
	""" Set or get white balance mode """
	global _wb_mode
	if val is not None:
		_wb_mode = val
	return _wb_mode

def agc_gain      (val=None):
	""" Set or get automatic gain control"""
	global _agc_gain
	if val is not None:
		_agc_gain = val
	return _agc_gain

def gainceiling   (val=None):
	""" Set or get gain ceilling """
	global _gainceiling
	if val is not None:
		_gainceiling = val
	return _gainceiling

def brightness    (val=None):
	""" Set or get brightness """
	global _brightness
	if val is not None:
		_brightness = val
	return _brightness

def contrast      (val=None):
	""" Set or get contrast """
	global _contrast
	if val is not None:
		_contrast  = val
	return _contrast

def saturation    (val=None):
	""" Set or get saturation """
	global _saturation
	if val is not None:
		_saturation = val
	return _saturation

def sharpness     (val=None):
	""" Set or get sharpness """
	global _sharpness
	if val is not None:
		_sharpness = val
	return _sharpness

def ae_level      (val=None):
	""" Set or get auto exposure level """
	global _ae_level
	if val is not None:
		_ae_level = val
	return _ae_level

def denoise       (val=None):
	""" Set or get denoise """
	global _denoise
	if val is not None:
		_denoise = val
	return _denoise

def whitebal      (val=None):
	""" Set or get white balance """
	global _whitebal
	if val is not None:
		_whitebal = val
	return _whitebal

def awb_gain      (val=None):
	""" Set or get automatic white balance gain"""
	global _awb_gain
	if val is not None:
		_awb_gain = val
	return _awb_gain

def exposure_ctrl (val=None):
	""" Set or get exposure control """
	global _exposure_ctrl
	if val is not None:
		_exposure_ctrl = val
	return _exposure_ctrl

def aec2          (val=None):
	""" Set or get auto exposure control 2"""
	global _aec2
	if val is not None:
		_aec2 = val
	return _aec2

def gain_ctrl     (val=None):
	""" Set or get gain control """
	global _gain_ctrl
	if val is not None:
		_gain_ctrl = val
	return _gain_ctrl

def bpc           (val=None):
	""" Set or get black pixel correction """
	global _bpc
	if val is not None:
		_bpc = val
	return _bpc

def wpc           (val=None):
	""" Set or get white pixel correction """
	global _wpc
	if val is not None:
		_wpc = val
	return _wpc

def raw_gma       (val=None):
	""" Set or get raw gma """
	global _raw_gma
	if val is not None:
		_raw_gma = val
	return _raw_gma

def lenc          (val=None):
	""" Set or get lenc """
	global _lenc
	if val is not None:
		_lenc = val
	return _lenc

def hmirror       (val=None):
	""" Set or get horizontal mirror """
	global _hmirror
	if val is not None:
		_hmirror = val
	return _hmirror

def vflip         (val=None):
	""" Set or get vertical flip """
	global _vflip
	if val is not None:
		_vflip = val
	return _vflip

def dcw           (val=None):
	""" Set or get downsize EN """
	global _dcw
	if val is not None:
		_dcw = val
	return _dcw

def colorbar      (val=None):
	""" Set or get color bar """
	global _colorbar
	if val is not None:
		_colorbar = val
	return _colorbar

def isavailable():
	""" Indicates if the camera module is available or not """
	return True

def flash(level):
	""" Set the flash level """
