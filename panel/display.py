from panel.max7219 import Lcd


class Display:

# Display 1 Mapping
	NAV = 2
	VOR = 1
	ILS = 4
	MLS = 8
	ADF = 16
	BFO = 32

# Display 2 Mapping
	VHF1 = 1
	VHF2 = 2
	VHF3 = 4
	HF1  = 8
	HF2  = 16
	AM   = 32

	def __init__(self):
		# Setup 2 LCD displays with each having 6 digits
		self.lcd = Lcd(400000, 2)
		self.lcd.setMode(0,Lcd.NORMAL)
		self.lcd.setMode(1,Lcd.NORMAL)
		self.lcd.setIntensity(0,15)
		self.lcd.setIntensity(0,15)
		self.lcd.setMaxDigits(0,7)
		self.lcd.setMaxDigits(1,7)
		self.lcd.setDecodeModeForDigits(0,[0,1,2,3,4,5])
		self.lcd.setDecodeModeForDigits(1,[0,1,2,3,4,5])
		self.lcd.setDigitString(0,"------")
		self.lcd.setDigitString(1,"------")
		self.lcd.setDigitValue(0, 6,0)
		self.lcd.setDigitValue(1, 6,0)

	def setActiveFrequency(self, freq):
		self.lcd.setValueString(0,freq)

	def setStbyFrequency(self, freq):
		self.lcd.setValueString(1,freq)

	def selectStbyNavMode(self, mode):
		self.lcd.setDigitValue(0,6,mode)

	def selectActiveMode(self, mode):
		self.lcd.setDigitValue(1,6,mode)

	def setBrightness(self, b):
		self.lcd.setIntensity(0,b)
		self.lcd.setIntensity(1,b)

