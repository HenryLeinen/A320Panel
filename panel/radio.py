from configparser import ConfigParser
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
	MODE_HF1  = 17
	MODE_HF2  = 18


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
		# Initialize the config file parser
		self.cfg = ConfigParser()
		# load the config file
		self.cfg.read('panel/xplane.cfg')
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
			"com2_stdby_freq": 109.5,
			"com3_freq": 1.00,
			"com3_stdby_freq": 1.0,
			"hf1_freq": 1.20,
			"hf1_stdby_freq": 2.825,
			"hf2_freq": 12.025,
			"hf2_stdby_freq": 1.025,
		}
		self.fmt_string = {
			"vor_freq":			' {:03.2f}',
			"vor_stdby_freq":	' {:03.2f}',
			"vor_course":		'C-{:03f}',
			"ils_freq": 		' {:03.2f}',
			"ils_stdby_freq": 	' {:03.2f}',
			"ils_course": 		'C-{:03f}',
			"adf1_freq": 		' {:04.1f}',
			"adf1_stdby_freq": 	' {:04.1f}',
			"adf2_freq": 		' {:04.1f}',
			"adf2_stdby_freq": 	' {:04.1f}',
			"com1_freq":		'{:03.3f}',
			"com1_stdby_freq":	'{:03.3f}',
			"com2_freq":		'{:03.3f}',
			"com2_stdby_freq": 	'{:03.3f}',
			"com3_freq":		' ACARS',
			"com3_stdby_freq":	'13232',
			"hf1_freq":			'{:>6.2f}',
			"hf1_stdby_freq":	'{:>6.2f}',
			"hf2_freq":			'{:>6.2f}',
			"hf2_stdby_freq":	'{:>6.2f}',
		}

		# Initialize the xplane receiver
		self.xplane = xplane()
		self.xplane.start()
		# Setup callbacks for server variable changes as needed
		self.xplane.setCallback("com1_freq", self.cbkFrequencyValueChanged)
		self.xplane.setCallback("com2_freq", self.cbkFrequencyValueChanged)
		self.xplane.setCallback("com1_stdby_freq", self.cbkFrequencyValueChanged)
		self.xplane.setCallback("com2_stdby_freq", self.cbkFrequencyValueChanged)
		self.xplane.setCallback("ils_freq", self.cbkFrequencyValueChanged)
		self.xplane.setCallback("ils_stdby_freq", self.cbkFrequencyValueChanged)
		self.xplane.setCallback("vor_freq", self.cbkFrequencyValueChanged)
		self.xplane.setCallback("vor_stdby_freq", self.cbkFrequencyValueChanged)
		self.xplane.setCallback("adf1_freq", self.cbkFrequencyValueChanged)
		self.xplane.setCallback("adf2_freq", self.cbkFrequencyValueChanged)
		self.xplane.setCallback("adf1_stdby_freq", self.cbkFrequencyValueChanged)
		self.xplane.setCallback("adf2_stdby_freq", self.cbkFrequencyValueChanged)
		# setup the keyboard and register the callback
		self.keyboard = Keyboard( [0,5,6,13], [4,3,2,19])
		self.keyboard.registerCallbacks(self.onKeyPressed, 0)
		self.keyboard.start()
		# setup the OnOffSwitch
		self.OnOff = OnOffSwitch(26, self.OnOffChanged)
		self.OnOffChanged(self.OnOff.getState())
		# store the nav override mode. This is on when the user has pressed the NAV button. The modification of VOR, ILS is only possible in NAV override mode
		self.NavOverride = False 
		# store the last valid COM Mode, to return to after NAV button was pressed a second time
		self.LastComMode = self.MODE_NAV1
		# remember if we were in VOR/ILS Course editing mode
		self.VorCourseEditingActive = False
		self.IlsCourseEditingActive = False

	def OnOffChanged(self, newval):
		if newval == 0:
			# switch the panel off
			self.display.enable(False)
		else:
			# switch the panel on
			self.display.enable(True)

	def cbkFrequencyValueChanged(self, idx, newval):
		self.frequencies[idx] = newval
		self.update()

	def onKeyPressed(self, key):
		if self.OnOff.getState() == False:
			return
		if key == Keyboard.BTN_NAV:
			if self.NavOverride == False:
				self.LastComMode = self.Mode
				self.NavOverride = True
			else:
				self.Mode = self.LastComMode
				self.NavOverride = False
		if key == Keyboard.BTN_VHF1:
			self.Mode = self.MODE_COM1
			self.NavOverride = False
		elif key == Keyboard.BTN_VHF2:
			self.Mode = self.MODE_COM2
			self.NavOverride = False
		elif key == Keyboard.BTN_VHF3:
			self.Mode = self.MODE_COM3
			self.NavOverride = False
		elif key == Keyboard.BTN_VOR:
			if self.NavOverride == True:
				self.Mode = self.MODE_NAV2
		elif key == Keyboard.BTN_ILS:
			if self.NavOverride == True:
				self.Mode = self.MODE_NAV1
		elif key == Keyboard.BTN_ADF:
			if self.NavOverride == True:
				self.Mode = self.MODE_ADF2
		elif key == Keyboard.BTN_MLS:
			if self.NavOverride == True:
				self.Mode = self.MODE_ADF1
		elif key == Keyboard.BTN_HF1:
			self.Mode = self.MODE_HF1
			self.NavOverride = False
		elif key == Keyboard.BTN_HF2:
			self.Mode = self.MODE_HF2
			self.NavOverride = False
		elif key == Keyboard.BTN_XCHG:
			# exchange standby frequency with active frequency
			freq = self.getActiveFrequency()
			freq_2 = self.getStandbyFrequency()
			if self.Mode == self.MODE_NAV1:
				if self.IlsCourseEditingActive == True:
					self.IlsCourseEditingActive = False
				else:
					self.IlsCourseEditingActive = True
			elif self.Mode == self.MODE_NAV2:
				if self.VorCourseEditingActive == True:
					self.VorCourseEditingActive = False
				else:
					self.VorCourseEditingActive = True
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
		elif self.Mode == self.MODE_HF1:
			key = "hf1_stdby_freq"
		elif self.Mode == self.MODE_HF2:
			key = "hf2_stdby_freq"
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
		elif self.Mode == self.MODE_HF1:
			key = "hf1_freq"
		elif self.Mode == self.MODE_HF2:
			key = "hf2_freq"
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
		t_key = 'Var.{}'.format(key)
		if self.incMode == 0:
			incr = -float(self.cfg[t_key]["increment_lo"])
		else:
			incr = -float(self.cfg[t_key]["increment_hi"])
		maxfreq = float(self.cfg[t_key]["range_in_max"])
		minfreq = float(self.cfg[t_key]["range_in_min"])
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
		t_key = 'Var.{}'.format(key)
		if self.incMode == 0:
			incr = float(self.cfg[t_key]["increment_lo"])
		else:
			incr = float(self.cfg[t_key]["increment_hi"])
		maxfreq = float(self.cfg[t_key]["range_in_max"])
		minfreq = float(self.cfg[t_key]["range_in_min"])
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
			self.display.setActiveText(self.fmt_string["ils_freq"], float(self.frequencies["ils_freq"]))
			self.display.setStandbyText(self.fmt_string["ils_stdby_freq"], float(self.frequencies["ils_stdby_freq"]))
			self.display.selectActiveMode(Display.ILS|Display.NAV)
		elif mode == self.MODE_NAV2:
			self.display.setActiveText(self.fmt_string["vor_freq"], float(self.frequencies["vor_freq"]))
			self.display.setStandbyText(self.fmt_string["vor_stdby_freq"], float(self.frequencies["vor_stdby_freq"]))
			self.display.selectActiveMode(Display.VOR|Display.NAV)
		elif mode == self.MODE_COM1:
			self.display.setActiveText(self.fmt_string["com1_freq"], float(self.frequencies["com1_freq"]))
			self.display.setStandbyText(self.fmt_string["com1_stdby_freq"], float(self.frequencies["com1_stdby_freq"]))
			self.display.selectStbyNavMode(Display.VHF1)
		elif mode == self.MODE_COM2:
			self.display.setActiveText(self.fmt_string["com2_freq"], float(self.frequencies["com2_freq"]))
			self.display.setStandbyText(self.fmt_string["com2_stdby_freq"], float(self.frequencies["com2_stdby_freq"]))
			self.display.selectStbyNavMode(Display.VHF2)
		elif mode == self.MODE_COM3:
			self.display.setActiveText(self.fmt_string["com3_freq"], float(self.frequencies["com3_freq"]))
			self.display.setStandbyText(self.fmt_string["com3_stdby_freq"], float(self.frequencies["com3_stdby_freq"]))
			self.display.selectStbyNavMode(Display.VHF3)
		elif mode == self.MODE_ADF1:
			self.display.setActiveText(self.fmt_string["adf1_freq"], float(self.frequencies["adf1_freq"]))
			self.display.setStandbyText(self.fmt_string["adf1_stdby_freq"], float(self.frequencies["adf1_stdby_freq"]))
			self.display.selectActiveMode(Display.MLS)
		elif mode == self.MODE_ADF2:
			self.display.setActiveText(self.fmt_string["adf2_freq"], float(self.frequencies["adf2_freq"]))
			self.display.setStandbyText(self.fmt_string["adf2_stdby_freq"], float(self.frequencies["adf2_stdby_freq"]))
			self.display.selectActiveMode(Display.ADF)
		elif mode == self.MODE_HF1:
			self.display.setActiveText(self.fmt_string["hf1_freq"], float(self.frequencies["hf1_freq"]))
			self.display.setStandbyText(self.fmt_string["hf1_stdby_freq"], float(self.frequencies["hf1_stdby_freq"]))
			self.display.selectActiveMode(Display.HF1)
		elif mode == self.MODE_HF2:
			self.display.setActiveText(self.fmt_string["hf2_freq"], float(self.frequencies["hf2_freq"]))
			self.display.setStandbyText(self.fmt_string["hf2_stdby_freq"], float(self.frequencies["hf2_stdby_freq"]))
			self.display.selectActiveMode(Display.HF2)
		else:
			self.display.clearActiveFrequency()
			self.display.clearStbyFrequency()
			self.display.selectActiveMode(Display.CLR)
			self.display.selectStbyNavMode(Display.CLR)

	# Update the displays and the LEDs
	def update(self):
		if self.NavOverride == True:
			self.display.selectActiveMode(Display.NAV)
		if self.Mode == self.MODE_NAV1:
			print ("Mode is ILS")
			if self.IlsCourseEditingActive == False:
				self.display.setActiveText(self.fmt_string["ils_freq"], float(self.frequencies["ils_freq"]))
				self.display.setStandbyText(self.fmt_string["ils_stdby_freq"], float(self.frequencies["ils_stdby_freq"]))
			else:
				self.display.setActiveText(self.fmt_string["ils_freq"], float(self.frequencies["ils_freq"]))
				self.display.setStandbyText(self.fmt_string["ils_course"], float(self.frequencies["ils_course"]))
			self.display.selectActiveMode(Display.ILS|Display.NAV)
			self.display.selectStbyNavMode(Display.NONE)
		elif self.Mode == self.MODE_NAV2:
			print ("Mode is VOR")
			if self.VorCourseEditingActive == False:
				self.display.setActiveText(self.fmt_string["vor_freq"], float(self.frequencies["vor_freq"]))
				self.display.setStandbyText(self.fmt_string["vor_stdby_freq"], float(self.frequencies["vor_stdby_freq"]))
			else:
				self.display.setActiveText(self.fmt_string["vor_freq"], float(self.frequencies["vor_freq"]))
				self.display.setStandbyText(self.fmt_string["vor_course"], float(self.frequencies["vor_course"]))
			self.display.selectActiveMode(Display.VOR|Display.NAV)
			self.display.selectStbyNavMode(Display.NONE)
		elif self.Mode == self.MODE_COM1:
			print ("Mode is VHF1")
			self.display.setActiveText(self.fmt_string["com1_freq"], float(self.frequencies["com1_freq"]))
			self.display.setStandbyText(self.fmt_string["com1_stdby_freq"], float(self.frequencies["com1_stdby_freq"]))
			self.display.selectStbyNavMode(Display.VHF1)
			if self.NavOverride == True:
				self.display.selectActiveMode(Display.NAV)
			else:
				self.display.selectActiveMode(Display.NONE)
		elif self.Mode == self.MODE_COM2:
			print ("Mode is VHF2")
			self.display.setActiveText(self.fmt_string["com2_freq"], float(self.frequencies["com2_freq"]))
			self.display.setStandbyText(self.fmt_string["com2_stdby_freq"], float(self.frequencies["com2_stdby_freq"]))
			self.display.selectStbyNavMode(Display.VHF2)
			if self.NavOverride == True:
				self.display.selectActiveMode(Display.NAV)
			else:
				self.display.selectActiveMode(Display.NONE)
		elif self.Mode == self.MODE_COM3:
			print ("Mode is VHF3")
			self.display.setActiveText(self.fmt_string["com3_freq"], float(self.frequencies["com3_freq"]))
			self.display.setStandbyText(self.fmt_string["com3_stdby_freq"], float(self.frequencies["com3_stdby_freq"]))
			self.display.selectStbyNavMode(Display.VHF3)
			if self.NavOverride == True:
				self.display.selectActiveMode(Display.NAV)
			else:
				self.display.selectActiveMode(Display.NONE)
		elif self.Mode == self.MODE_HF1:
			print ("Mode is HF1")
			self.display.setActiveText(self.fmt_string["hf1_freq"], float(self.frequencies["hf1_freq"]))
			self.display.setStandbyText(self.fmt_string["hf1_stdby_freq"], float(self.frequencies["hf1_stdby_freq"]))
			self.display.selectStbyNavMode(Display.HF1)
			if self.NavOverride == True:
				self.display.selectActiveMode(Display.NAV)
			else:
				self.display.selectActiveMode(Display.NONE)
		elif self.Mode == self.MODE_HF2:
			print ("Mode is HF2")
			self.display.setActiveText(self.fmt_string["hf2_freq"], float(self.frequencies["hf2_freq"]))
			self.display.setStandbyText(self.fmt_string["hf2_stdby_freq"], float(self.frequencies["hf2_stdby_freq"]))
			self.display.selectStbyNavMode(Display.HF2)
			if self.NavOverride == True:
				self.display.selectActiveMode(Display.NAV)
			else:
				self.display.selectActiveMode(Display.NONE)
		elif self.Mode == self.MODE_ADF1:
			print ("Mode is MLS")
			self.display.setActiveText(self.fmt_string["adf1_freq"], float(self.frequencies["adf1_freq"]))
			self.display.setStandbyText(self.fmt_string["adf1_stdby_freq"], float(self.frequencies["adf1_stdby_freq"]))
			self.display.selectActiveMode(Display.MLS|Display.NAV)
			self.display.selectStbyNavMode(Display.NONE)
		elif self.Mode == self.MODE_ADF2:
			print ("Mode is ADF")
			self.display.setActiveText(self.fmt_string["adf2_freq"], float(self.frequencies["adf2_freq"]))
			self.display.setStandbyText(self.fmt_string["adf2_stdby_freq"], float(self.frequencies["adf2_stdby_freq"]))
			self.display.selectActiveMode(Display.ADF|Display.NAV)
			self.display.selectStbyNavMode(Display.NONE)
		else:
			self.display.clearActiveFrequency()
			self.display.clearStbyFrequency()
			self.display.selectActiveMode(Display.NONE)
			self.display.selectStbyNavMode(Display.NONE)


	def stop(self):
		self.display.enable(False)
		self.keyboard.stop()
		self.xplane.stop()
		print ("...Radio terminated...")

