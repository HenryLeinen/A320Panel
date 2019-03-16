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
		self.max_digits = [1 for x in range(max_displays)]
		self.values		= [[ 0 for x in range(8)] for y in range(max_displays)]
		self.char_lookup = {
			'0':	0b01111110,
			'1': 	0b00110000,
			'2':	0b01101101,
			'3':	0b01111001,
			'4':	0b00110011,
			'5':	0b01011011,
			'6':	0b01011111,
			'7':	0b01110000,
			'8':	0b01111111,
			'9':	0b01111011,
			'-':	0b00000001,
			'C':	0b01001110,
			'E':	0b01001111,
			'H':	0b00110111,
			'A':	0b01110111,
			'R':	0b01100110,
			'S':	0b01011011,
			'L':	0b00001110,
			'P':	0b01100110,
			' ':	0b00000000
		}
		print (self.char_lookup)
		self.sendToAll([0x09, 0x00])

	# This function sends a tuple (16-bit) value to the display with number <devno>
	def send(self, devno, b):
		arr = []
		for i in range(self.max_displays):
			if i== devno:
				arr = arr + b
			else:
				arr = arr + [0x00, 0x00]
#		print ("***Lcd.send(devno={}, b={}, arr={}".format(devno, b, arr))
		self.spi.writebytes(arr)

	# This function send a tuple (16-bit) value to all displays at once
	def sendToAll(self, b):
		arr = []
		for i in range(self.max_displays):
			arr = arr + b
#		print ("***Lcd.sendAll(b={}, arr={}".format(b, arr))
		self.spi.writebytes(arr)

	# This function sets the given mode to all displays. Can be either NORMAL, TEST or SHUTDOWN
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

	# This function sets the given mode for the given display <devno>. Can be either NORMAL, TEST or SHUTDOWN
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

	# This function sets the brightness of all displays at once
	def setIntensityAll(self, intensity):
		self.sendToAll([0x0a, intensity])

	# This function set the brightness of the given display <devno>
	def setIntensity(self, devno, intensity):
		self.send(devno, [0x0a, intensity])

	# This function sets the decode mode for the given display using the provided list of digits
#	def setDecodeModeForDigits(self, devno, digitlist):
#		digits = 0
#		print ("Activating digits : ")
#		for i,d in enumerate(digitlist):
#			print (" ", d)
#			digits = digits | 2**d
#		self.send(devno, [0x09, digits])

	# Sets the maximum number of digits for the given display <devno>
	def setMaxDigits(self, devno, maxdigit):
		self.max_digits[devno] = maxdigit
		self.send(devno, [0x0b, maxdigit-1])

	# Sets the a single digit of display <devno> to the given raw value. The function will not actually flush the values
	# if the parameter <flush> is false.
	def setDigitValue(self, devno, d, v, flush=False):
		self.values[devno][d] = v
		if flush== True:
			self.sendAll(devno)

	# Flushes the current buffers to the given display
	def sendAll(self, devno):
#		print ("***Lcd.sendAll(devno={})".format(devno))
		for i in range(8):
			self.send(devno, [i+1, self.values[devno][i]])

	# Sets a specific digits to given values. This is given as an array of <index, value> pairs
	def setDigitValues(self, devno, vals):
		for i,d in enumerate(vals):
			self.values[devno][i] = d
		self.sendAll(devno)

	# Sets a string to device <devno>, using the internal lookup table
	def setDigitString(self, devno, dv):
		i = 0
		for v in dv:
			if v in self.char_lookup.keys():
				self.values[devno][i] = self.char_lookup[v]
				i = i + 1
			elif v == '.':
				self.values[devno][i-1] = self.values[devno][i-1]+128
			else:
				self.values[devno][i] = v
#		print ("*****", self.values[devno])
		self.sendAll(devno)

	def close(self):
		self.spi.close()


