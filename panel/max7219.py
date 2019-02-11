import spidev
import time


def get_digit(number, digit):
	return int(number // 10**digit %10)


class Lcd:

	TEST = 1
	NORMAL = 2
	SHUTDOWN = 4

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
#		print ("***Lcd.send(devno={}, b={}, arr={}".format(devno, b, arr))
		self.spi.writebytes(arr)

	def sendToAll(self, b):
		arr = []
		for i in range(self.max_displays):
			arr = arr + b
#		print ("***Lcd.sendAll(b={}, arr={}".format(b, arr))
		self.spi.writebytes(arr)

	def setModeAll(self, mode):
		if mode == Lcd.NORMAL:
			self.sendToAll([0x0c,0x01])
			self.sendToAll([0x0f,0x00])
		elif mode == Lcd.TEST:
			self.sendToAll([0x0f,0x01])
			self.sendToAll([0x0c,0x01])
		else:
			self.sendToAll([0x0c,0x00])
			self.sendToAll([0x0f,0x00])

	def setMode(self, devno, mode):
		if mode == Lcd.NORMAL:
			self.send(devno, [0x0f, 0x00])
			self.send(devno, [0x0c, 0x01])
		elif mode == Lcd.TEST:
			self.send(devno, [0x0f, 0x01])
			self.send(devno, [0x0c, 0x01])
		else:
			self.send(devno, [0x0f, 0x00])
			self.send(devno, [0x0c, 0x00])

	def setIntensityAll(self, intensity):
		self.sendToAll([0x0a, intensity])

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
#		print ("***Lcd.sendAll(devno={})".format(devno))
		for i in range(8):
			self.send(devno, [i+1, self.values[devno][i]])

	def setDigitValues(self, devno, vals):
		for i,d in enumerate(vals):
			self.values[devno][i] = d
		self.sendAll(devno)

	def setDigitString(self, devno, dv):
		i = 0
#		print("***Lcd.setDigitString (devno={}, dv={})".format(devno, dv))
		for v in dv:
#			print("****v={} (ord={})".format(v,ord(v)))
			if ord(v) in range(ord('0'),ord('9')+1):
				self.values[devno][i] = ord(v)-48
#				print (i, v)
				i = i + 1
			elif v == '-':
				self.values[devno][i] = 10
				i = i + 1
			elif v == 'E':
				self.values[devno][i] = 11
				i = i + 1
			elif v == 'H':
				self.values[devno][i] = 12
				i = i + 1
			elif v == 'L':
				self.values[devno][i] = 13
				i = i + 1
			elif v == 'P':
				self.values[devno][i] = 14
				i = i + 1
			elif v == ' ':
				self.values[devno][i] = 15
				i = i + 1
			elif v == '.':
				self.values[devno][i-1] = self.values[devno][i-1]+128
#				print (i, v)
#		print ("*****", self.values[devno])
		self.sendAll(devno)

	def close(self):
		self.spi.close()


