from panel.display import Display
from panel.max7219 import Lcd
from panel.encoder import Encoder
from panel.xplane import xplane
from panel.keymatrix import Keyboard
from panel.onoffswitch import OnOffSwitch

class Radio:

	MODE_NAV1 = 0			# ILS
	MODE_NAV2 = 1			# VOR
	MODE_COM1 = 2
	MODE_COM2 = 3
	MODE_COM3 = 15			# no standard x-plane value known
	MODE_ADF1 = 4			# MLS
	MODE_ADF2 = 5			# ADF2
	MODE_MLF = 16			# no standard x-plane value known
	MODE_OFF  = 10


	def __init__(self):
		self.active = True
		# set the radio mode to MODE_NAV1 per default
		self.Mode = Radio.MODE_NAV1
		# set the increment mode : a value of zero means a small increment on rotary encoder changes, a value of 1 means large increments
		self.incMode = 0
		# create the display (LCD + LEDs) device
		self.display = Display()
		# create the rotary encoder device and register the callbacks
		self.encoder = Encoder(17, 27, 22)
		self.encoder.registerLeftEvent(self.onEncoderLeft)
		self.encoder.registerRightEvent(self.onEncoderRight)
		self.encoder.registerButtonPressedEvent(self.onEncoderButtonPressed)
		# setup the internal datastructures
		self.frequencies = {
			"vor_freq": 112.00,
			"vor_stdby_freq":	112.00,
			"vor_course":	0.0,
			"ils_freq": 109.00,
			"ils_stdby_freq": 109.00,
			"ils_course": 10.0,
			"adf1_freq": 110,
			"adf1_stdby_freq": 111,
			"adf2_freq": 112,
			"adf2_stdby_freq": 113,
			"com1_freq": 108.00,
			"com1_stdby_freq": 108.5,
			"com2_freq": 109.00,
			"com2_stdby_freq": 109.5
		}
		self.min_vals = {
			"vor_stdby_freq":	111.97,
			"vor_course":	0.0,
			"ils_stdby_freq": 108.10,
			"ils_course": 0.0,
			"adf1_stdby_freq": 0,
			"adf2_stdby_freq": 0,
			"com1_stdby_freq": 118.0,
			"com2_stdby_freq": 118.0
		}
		self.max_vals = {
			"vor_stdby_freq":	117.95,
			"vor_course":	359.9,
			"ils_stdby_freq": 111.95,
			"ils_course": 359.9,
			"adf1_stdby_freq": 0,
			"adf2_stdby_freq": 0,
			"com1_stdby_freq": 136.9,
			"com2_stdby_freq": 136.9
		}
		self.increment_lo = {
			"vor_stdby_freq":	0.25,
			"vor_course":	1.0,
			"ils_stdby_freq": 0.25,
			"ils_course": 1.0,
			"adf1_stdby_freq": 1,
			"adf2_stdby_freq": 1,
			"com1_stdby_freq": 0.25,
			"com2_stdby_freq": 0.25
		}
		self.increment_hi = {
			"vor_stdby_freq":	0.5,
			"vor_course":	5.0,
			"ils_stdby_freq": 0.5,
			"ils_course": 5.0,
			"adf1_stdby_freq": 10,
			"adf2_stdby_freq": 10,
			"com1_stdby_freq": 1.0,
			"com2_stdby_freq": 1.0
		}

		# Initialize the xplane receiver
		self.xplane = xplane()
		self.xplane.start()
		# TODO: Setup callbacks as needed
		# setup the keyboard and register the callback
		self.keyboard = Keyboard( [0,5,6,13], [4,3,2,19])
		self.keyboard.registerCallbacks(self.onKeyPressed, 0)
		self.keyboard.start()
		# setup the OnOffSwitch
		self.OnOff = OnOffSwitch(26, self.OnOffChanged)
		self.OnOffChanged(self.OnOff.getState())

	def OnOffChanged(self, newval):
		if newval == 0:
			# switch the panel off
			self.display.enable(False)
		else:
			# switch the panel on
			self.display.enable(True)

	def onKeyPressed(self, key):
		if self.OnOff.getState() == False:
			return
		if key == Keyboard.BTN_VHF1:
			self.Mode = self.MODE_COM1
		elif key == Keyboard.BTN_VHF2:
			self.Mode = self.MODE_COM2
		elif key == Keyboard.BTN_VOR:
			self.Mode = self.MODE_NAV2
		elif key == Keyboard.BTN_ILS:
			self.Mode = self.MODE_NAV1
		elif key == Keyboard.BTN_ADF:
			self.Mode = self.MODE_ADF2
		elif key == Keyboard.BTN_MLS:
			self.Mode = self.MODE_ADF1
		elif key == Keyboard.BTN_XCHG:
			# exchange standby frequency with active frequency
			freq = self.getActiveFrequency()
			freq_2 = self.getStandbyFrequency()
			self.setActiveFrequency(freq_2)
			self.setStandbyFrequency(freq)
		self.update()


	def getStandbyFrequencyKey(self):
		if self.Mode == self.MODE_NAV1:
			key = "vor_stdby_freq"
		elif self.Mode == self.MODE_NAV2:
			key = "ils_stdby_freq"
		elif self.Mode == self.MODE_ADF1:
			key = "adf1_stdby_freq"
		elif self.Mode == self.MODE_ADF2:
			key = "adf2_stdby_freq"
		elif self.Mode == self.MODE_COM1:
			key = "com1_stdby_freq"
		elif self.Mode == self.MODE_COM2:
			key = "com2_stdby_freq"
		return key

	def getActiveFrequencyKey(self):
		if self.Mode == self.MODE_NAV1:
			key = "vor_freq"
		elif self.Mode == self.MODE_NAV2:
			key = "ils_freq"
		elif self.Mode == self.MODE_ADF1:
			key = "adf1_freq"
		elif self.Mode == self.MODE_ADF2:
			key = "adf2_freq"
		elif self.Mode == self.MODE_COM1:
			key = "com1_freq"
		elif self.Mode == self.MODE_COM2:
			key = "com2_freq"
		return key

	def getStandbyFrequency(self):
		return self.frequencies[self.getStandbyFrequencyKey()]

	def setStandbyFrequency(self, freq):
		self.frequencies[self.getStandbyFrequencyKey()] = freq

	def getActiveFrequency(self):
		return self.frequencies[self.getActiveFrequencyKey()]

	def setActiveFrequency(self, freq):
		self.frequencies[self.getActiveFrequencyKey()] = freq

	def onEncoderLeft(self):
		if self.OnOff.getState() == False:
			return
		# Decrement the frequency
		key = self.getStandbyFrequencyKey()
		if self.incMode == 0:
			incr = -self.increment_lo[key]
		else:
			incr = -self.increment_hi[key]
		maxfreq = self.max_vals[key]
		minfreq = self.min_vals[key]
		freq = self.frequencies[key] + incr
		if freq < minfreq:
			freq = maxfreq
		elif freq > maxfreq:
			freq = minfreq
#		print ("*** New value {} is {}".format(key, freq))
		self.frequencies[key] = freq
		# Send frequency
		self.xplane.setValue(key, freq)
		self.update()

	def onEncoderRight(self):
		if self.OnOff.getState() == False:
			return
		# Increment the frequency
		key = self.getStandbyFrequencyKey()
		if self.incMode == 0:
			incr = self.increment_lo[key]
		else:
			incr = self.increment_hi[key]
		maxfreq = self.max_vals[key]
		minfreq = self.min_vals[key]
		freq = self.frequencies[key] + incr
		if freq < minfreq:
			freq = maxfreq
		elif freq > maxfreq:
			freq = minfreq
#		print ("*** New value {} is {}".format(key, freq))
		self.frequencies[key] = freq
		# Send frequency
		self.xplane.setValue(key, freq)
		# Call setMode in order to display the new values
		self.update()

	def onEncoderButtonPressed(self):
		if self.OnOff.getState() == False:
			return
		if self.incMode == 0:
			self.incMode = 1
		else:
			self.incMode = 0

	# this function will update the mode LEDs as well as respective frequency displays
	def setMode(self, mode):
		print ("Mode is now %d" % mode)
		if mode == self.MODE_NAV1:
			self.display.setActiveFrequency(float(self.frequencies["vor_freq"]))
			self.display.setStbyFrequency(float(self.frequencies["vor_stdby_freq"]) )
			self.display.selectActiveMode(Display.ILS)
		elif mode == self.MODE_NAV2:
			self.display.setActiveFrequency(float(self.frequencies["ils_freq"]) )
			self.display.setStbyFrequency(float(self.frequencies["ils_stdby_freq"]))
			self.display.selectActiveMode(Display.VOR)
		elif mode == self.MODE_COM1:
			self.display.setActiveFrequency(float(self.frequencies["com1_freq"]))
			self.display.setStbyFrequency(float(self.frequencies["com1_stdby_freq"]))
			self.display.selectStbyNavMode(Display.VHF1)
		elif mode == self.MODE_COM2:
			self.display.setActiveFrequency(float(self.frequencies["com2_freq"]))
			self.display.setStbyFrequency(float(self.frequencies["com2_stdby_freq"]))
			self.display.selectStbyNavMode(Display.VHF2)
		elif mode == self.MODE_ADF1:
			self.display.setActiveFrequency(float(self.frequencies["adf1_freq"]))
			self.display.setStbyFrequency(float(self.frequencies["adf1_stdby_freq"]))
			self.display.selectActiveMode(Display.MLS)
		elif mode == self.MODE_ADF2:
			self.display.setActiveFrequency(float(self.frequencies["adf2_freq"]))
			self.display.setStbyFrequency(float(self.frequencies["adf2_stdby_freq"]))
			self.display.selectActiveMode(Display.ADF)
		else:
			self.display.clearActiveFrequency()
			self.display.clearStbyFrequency()
			self.display.selectActiveMode(Display.CLR)
			self.display.selectStbyNavMode(Display.CLR)

	# Update the displays and the LEDs
	def update(self):
		if self.Mode == self.MODE_NAV1:
			print ("Mode is ILS")
			self.display.setActiveFrequency(float(self.frequencies["vor_freq"]))
			self.display.setStbyFrequency(float(self.frequencies["vor_stdby_freq"]))
			self.display.selectActiveMode(Display.ILS)
		elif self.Mode == self.MODE_NAV2:
			print ("Mode is VOR")
			self.display.setActiveFrequency(float(self.frequencies["ils_freq"]) )
			self.display.setStbyFrequency(float(self.frequencies["ils_stdby_freq"] ))
			self.display.selectActiveMode(Display.VOR)
		elif self.Mode == self.MODE_COM1:
			print ("Mode is VHF1")
			self.display.setActiveFrequency(float(self.frequencies["com1_freq"]))
			self.display.setStbyFrequency(float(self.frequencies["com1_stdby_freq"]))
			self.display.selectStbyNavMode(Display.VHF1)
		elif self.Mode == self.MODE_COM2:
			print ("Mode is VHF2")
			self.display.setActiveFrequency(float(self.frequencies["com2_freq"]))
			self.display.setStbyFrequency(float(self.frequencies["com2_stdby_freq"]))
			self.display.selectStbyNavMode(Display.VHF2)
		elif self.Mode == self.MODE_COM3:
			print ("Mode is VHF3")
			self.display.setActiveFrequency(float(self.frequencies["com3_freq"]))
			self.display.setStbyFrequency(float(self.frequencies["com3_stdby_freq"]))
			self.display.selectStbyNavMode(Display.VHF3)
		elif self.Mode == self.MODE_ADF1:
			print ("Mode is MLS")
			self.display.setActiveFrequency(float(self.frequencies["adf1_freq"]))
			self.display.setStbyFrequency(float(self.frequencies["adf1_stdby_freq"]))
			self.display.selectActiveMode(Display.MLS)
		elif self.Mode == self.MODE_ADF2:
			print ("Mode is ADF")
			self.display.setActiveFrequency(float(self.frequencies["adf2_freq"]))
			self.display.setStbyFrequency(float(self.frequencies["adf2_stdby_freq"]))
			self.display.selectActiveMode(Display.ADF)
		else:
			self.display.clearActiveFrequency()
			self.display.clearStbyFrequency()
			self.display.selectActiveMode(Display.CLR)
			self.display.selectStbyNavMode(Display.CLR)


	def stop(self):
		self.display.enable(False)
		self.keyboard.stop()
		self.xplane.stop()
		print ("...Radio terminated...")

