""" Class to drive DAC module uda1334a I2S, stereo audio decoder module board """
import struct
import math
import io
import time
import machine
import gc
from machine import I2S, Pin

class Uda1334:
	""" Class to drive DAC module uda1334a I2S, stereo audio decoder module board """
	def __init__(self, sck=26, ws=25, sd=22):
		""" Constructor 
		BCLK (Bit Clock) : GPIO26
		LRCLK (Left/Right Clock) : GPIO25
		DATA : GPIO22
		"""
		self.sck = sck
		self.ws = ws
		self.sd = sd
		self.wave = None
		self.i2s = None

	def play(self, wave, rate, duration=10):
		""" Play sound wave """
		self.wave = wave
		self.i2s = I2S(0, sck=Pin(self.sck), ws=Pin(self.ws), sd=Pin(self.sd), mode=I2S.TX, bits=16, format=I2S.STEREO, rate=rate, ibuf=4096)

		t = 1/(rate/(len(wave.getvalue())/4))
		try:
			buf = bytearray(self.wave.getvalue())
			gc.disable()
			for i in range(int(duration/t)):
				self.i2s.write(buf)
		finally:
			gc.enable()
			self.i2s.deinit()

	def create_wave(self, frequency, shape):
		""" Create sound wave with frequency and shape of wave """
		if frequency > 100:
			rate = 100000
			step = rate//frequency
		else:
			step = 1000
			rate = step*frequency
		sample = io.BytesIO()
		shape(sample,step)
		return sample, rate

	def triangle(self, buf, step):
		""" Creates a triangle wave """
		inc = 65536//(step//2)
		for i in range(-(32767-inc), 32767, inc):
			buf.write(struct.pack("<h",i))
			buf.write(struct.pack("<h",-i))
		for i in range(32767-inc,-32767, -inc):
			buf.write(struct.pack("<h",i))
			buf.write(struct.pack("<h",-i))

	def sinus(self, buf, step):
		""" Creates a sine wave """
		inc = 100000//step
		for angle in range(0, 100000, inc):
			sample = math.cos(angle*(2*math.pi)/100000) * 32767	
			buf.write(struct.pack("<h",int(sample)))
			buf.write(struct.pack("<h",-int(sample)))

	def bits_frame(self, byte, bits, parity, stop):
		""" Returns the bits that compose a byte sent on a uart """
		result = [0]
		bits_count = 0

		data = int(byte)
		for i in range(bits):
			if data & 1:
				bits_count += 1
				result.append(1)
			else:
				result.append(0)
			if data <= 1:
				break
			data >>= 1

		if parity is not None:
			if parity == 1:
				if bits_count & 1:
					result.append(0)
				else:
					result.append(1)
			else:
				if bits_count & 1:
					result.append(1)
				else:
					result.append(0)

		if stop == 1:
			result.append(1)
		if stop == 2:
			result.append(1)
		return result

	def create_uart(self, data, baud, bits=7, parity=1, stop=1):
		""" Create uart wave """
		sample = io.BytesIO()
		rate = 100000
		for char in data:
			bitfield = self.bits_frame(char, bits, parity, stop)

			for bit in bitfield:
				if bit:
					for i in range(rate*2//baud):
						sample.write(struct.pack("<h",32767))
				else:
					for i in range(rate*2//baud):
						sample.write(struct.pack("<h",-32767))
		return sample, rate

	def play_raw(self, filename):
		""" Plays a file containing a sound wave in raw 44khz stereo format """
		buf = bytearray(4096)
		self.i2s = I2S(0, sck=Pin(self.sck), ws=Pin(self.ws), sd=Pin(self.sd), mode=I2S.TX, bits=16, format=I2S.STEREO, rate=44100, ibuf=4096)
		with open(filename,'rb') as file:
			try:
				gc.disable()
				i = 0
				while True:
					length = file.readinto(buf)
					if length == 0:
						break
					if length < len(buf):
						self.i2s.write(buf[:length])
						break
					else:
						self.i2s.write(buf)
					print(i)
					i += 1
			finally:
				gc.enable()
				self.i2s.deinit()

def test():
	""" Plays multiple frequencies and waveform """
	uda = Uda1334()
	for i in range(10,5000, 100):
		print("Sinus    %d hz"%i)
		wave,rate = uda.create_wave(frequency=i, shape=uda.sinus)
		uda.play(wave,rate,3)
		print("Triangle %d hz"%i)
		wave,rate = uda.create_wave(frequency=i, shape=uda.triangle)
		uda.play(wave,rate,3)

def calibration():
	""" Plays a sine wave at 1khz """
	uda = Uda1334()
	wave, rate = uda.create_wave(frequency=1000, shape=uda.sinus)
	uda.play(wave, rate, 600)

def test_uart():
	""" Plays a uart type wave at 9600 baud """
	uda = Uda1334()
	wave, rate = uda.create_uart(b"Hello world", 9600)
	uda.play(wave, rate, 600)

def test_raw():
	""" Play raw file """
	uda = Uda1334()
	uda.play_raw("/sd/ambience.wav")
