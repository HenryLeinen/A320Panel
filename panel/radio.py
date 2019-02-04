from panel.display import Display

class Radio:

	MODE_NAV1 = 0
	MODE_NAV2 = 1
	MODE_COM1 = 2
	MODE_COM2 = 3
	MODE_ADF1 = 4
	MODE_ADF2 = 5
	MODE_OFF  = 10


	def __init__(self):
		self.active = True
		self.Mode = Radio.MODE_NAV1
		self.nav1_freq_hz = 108.000
		self.nav2_freq_hz = 108.000
		self.com1_freq_hz = 108.000
		self.com2_freq_hz = 108.000
		self.adf1_freq_hz = 338
		self.adf2_freq_hz = 339
		self.dme_freq_hz  = 114.200
		self.nav1_stdby_freq_hz = 109.000
		self.nav2_stdby_freq_hz = 109.000
		self.com1_stdby_freq_hz = 109.000
		self.com2_stdby_freq_hz = 109.000
		self.adf1_stdby_freq_hz = 341.000
		self.adf2_stdby_freq_hz = 341.000
		self.dme_stdby_freq_hz = 115.000
		self.display = Display()
		self.display.clearActiveFrequency()
		self.display.clearStbyFrequency()

	def setActiveNav1(self, freq ):
		self.nav1_freq_hz = freq
		print ("New NAV1_FREQ_HZ received %03.3f" % freq)

	def setActiveAdf1(self, freq ):
		self.adf1_freq_hz = freq
		print ("New ADF1_FREQ_HZ received %03.3f" % freq)
		
	def setMode(self, mode):
		if mode == self.MODE_NAV1:
			self.display.setActiveFrequency(self.nav1_freq_hz)
			self.display.setStbyFrequency(self.nav1_stdby_freq_hz)
			self.display.selectActiveMode(Display.NAV)
		elif mode == self.MODE_NAV2:
			self.display.setActiveFrequency(self.nav2_freq_hz)
			self.display.setStbyFrequency(self.nav2_stdby_freq_hz)
			self.display.selectActiveMode(Display.VOR)
		elif mode == self.MODE_COM1:
			self.display.setActiveFrequency(self.com1_freq_hz)
			self.display.setStbyFrequency(self.com1_stdby_freq_hz)
			self.display.selectStbyNavMode(Display.VHF1)
		elif mode == self.MODE_COM2:
			self.display.setActiveFrequency(self.com2_freq_hz)
			self.display.setStbyFrequency(self.com2_stdby_freq_hz)
			self.display.selectStbyNavMode(Display.VHF2)
		elif mode == self.MODE_ADF1:
			self.display.setActiveFrequency(self.adf1_freq_hz)
			self.display.setStbyFrequency(self.adf1_stdby_freq_hz)
			self.display.selectStbyNavMode(Display.HF1)
		elif mode == self.MODE_ADF2:
			self.display.setActiveFrequency(self.adf2_freq_hz)
			self.display.setStbyFrequency(self.adf2_stdby_freq_hz)
			self.display.selectStbyNavMode(Display.HF2)
		else:
			self.display.clearActiveFrequency()
			self.display.clearStbyFrequency()
			self.display.selectActiveMode(Display.CLR)
			self.display.selectStbyNavMode(Display.CLR)


