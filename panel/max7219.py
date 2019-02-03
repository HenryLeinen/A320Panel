import spidev
import time
from enum import Enum


class Max7219Mode(Enum):
	TEST=1
	NORMAL=2
	SHUTDOWN=4

def get_digit(number, digit):
	return int(number // 10**digit %10)


class Lcd:
	
	def __init__(self, max_speed_hz, max_displays):
		self.spi = spidev.SpiDev()
		self.spi.open(0,0)
		self.spi.max_speed_hz	= max_speed_hz
		self.spi.lsbfirst	= False
		self.spi.mode		= 0b00
		self.spi.bits_per_word	= 8
		self.spi.cshigh		= True
		self.max_displays	= max_displays
		self.values		= [[ 0 for x in range(8)] for y in range(max_displays)]


	def send(self, devno, b):
		arr = []
		for i in range(self.max_displays):
			if i== devno:
				arr = arr + b
			else:
				arr = arr + [0x00, 0x00]
		self.spi.writebytes(arr)

	def setMode(self, devno, mode):
		if mode == Max7219Mode.NORMAL:
			self.send(devno, [0x0f, 0x00])
			self.send(devno, [0x0c, 0x01])
		elif mode == Max7219Mode.TEST:
			self.send(devno, [0x0f, 0x01])
			self.send(devno, [0x0c, 0x01])
		else:
			self.send(devno, [0x0f, 0x00])
			self.send(devno, [0x0c, 0x00])

	def setIntensity(self, devno, intensity):
		self.send(devno, [0x0a, intensity])

	def setDecodeModeForDigits(self, devno, digitlist):
		digits = 0
		print ("Activating digits : ")
		for i,d in enumerate(digitlist):
			print (" ", d)
			digits = digits | 2**d
		self.send(devno, [0x09, digits])

	def setMaxDigits(self, devno, maxdigit):
		self.send(devno, [0x0b, maxdigit-1])

	def setDigitValue(self, devno, d, v):
		self.values[devno][d] = v
		self.sendAll(devno)

	def sendAll(self, devno):
		for i in range(8):
			self.send(devno, [i+1, self.values[devno][i]])

	def setDigitValues(self, devno, vals):
		for i,d in enumerate(vals):
			self.values[devno][i] = d
		self.sendAll(devno)

	def setDigitString(self, devno, dv):
		i = 0
		print (dv)
		for v in dv:
			if v in range(0,9):
				self.values[devno][i] = ord(v)-48
				print (i, v)
				i = i + 1
			elif v == '-':
				self.values[devno][i] = 10
			elif v == 'E':
				self.values[devno][i] = 11
			elif v == 'H':
				self.values[devno][i] = 12
			elif v == 'L':
				self.values[devno][i] = 13
			elif v == 'P':
				self.values[devno][i] = 14
			elif v == ' ':
				self.values[devno][i] = 15
			elif v == '.':
				self.values[devno][i-1] = self.values[devno][i-1]+128
		self.sendAll(devno)

	def close(self):
		self.spi.close()


