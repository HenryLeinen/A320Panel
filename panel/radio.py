from panel.display import Display
from panel.max7219 import Lcd
from panel.encoder import Encoder
from panel.xplane import XPlaneReceiver
from panel.keymatrix import Keyboard


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
		# set the radio mode to MODE_NAV1 per default
		self.Mode = Radio.MODE_NAV1
		# setup a dictionary of radio frequency values as x-plane keys with their frequencies
		self.variables = {  "sim/cockpit/radios/nav1_freq_hz":10800, 
							"sim/cockpit/radios/nav2_freq_hz":10800,
							"sim/cockpit/radios/com1_freq_hz":10820,
							"sim/cockpit/radios/com2_freq_hz":10820,
							"sim/cockpit/radios/adf1_freq_hz":33800,
							"sim/cockpit/radios/adf2_freq_hz":33900,
							"sim/cockpit/radios/dme_freq_hz":10900,
							"sim/cockpit/radios/nav1_stdby_freq_hz":10810,
							"sim/cockpit/radios/nav2_stdby_freq_hz":10810,
							"sim/cockpit/radios/com1_stdby_freq_hz":10830,
							"sim/cockpit/radios/com2_stdby_freq_hz":10830,
							"sim/cockpit/radios/adf1_stdby_freq_hz":34000,
							"sim/cockpit/radios/adf2_stdby_freq_hz":34010,
							"sim/cockpit/radios/dme_stdby_freq_hz":10810
							}
		# create the display (LCD + LEDs) device
		self.display = Display()
		# create the rotary encoder device and register the callbacks
		self.encoder = Encoder(17, 27, 22)
		self.encoder.registerLeftEvent(self.onEncoderLeft)
		self.encoder.registerRightEvent(self.onEncoderRight)
		# initialize an empty receiver. the receiver can only be created once a hostname and a port is known
		self.receiver = 0
		# setup the keyboard and register the callback
		self.keyboard = Keyboard( [0,5,6,13], [4,3,2,19])
		self.keyboard.registerCallbacks(self.onKeyPressed, 0)
		self.keyboard.start()


	def onKeyPressed(self, key):
		if key == Keyboard.BTN_VHF1:
			self.Mode = self.MODE_COM1
		elif key == Keyboard.BTN_VHF2:
			self.Mode = self.MODE_COM2
		elif key == Keyboard.BTN_VOR:
			self.Mode = self.MODE_NAV1
		elif key == Keyboard.BTN_ILS:
			self.Mode = self.MODE_NAV2
		elif key == Keyboard.BTN_ADF:
			self.Mode = self.MODE_ADF1
		elif key == Keyboard.BTN_MLS:
			self.Mode = self.MODE_ADF2
		elif key == Keyboard.BTN_XCHG:
			# exchange standby frequency with active frequency
			freq = self.getActiveFrequency()
			freq_2 = self.getStandbyFrequency()
			self.setActiveFrequency(freq_2)
			self.setStandbyFrequency(freq)
			self.receiver.sendValue(self.getActiveFrequencyKey(), freq_2)
			self.receiver.sendValue(self.getStandbyFrequencyKey(), freq)
		self.receiver.sendValue("sim/cockpit/radios/nav_com_adf_mode", self.Mode)

	def startReceiver(self, hostname, hostport):
		# create a new receiver object for the provided host and register the callback to be informed about incoming value updates
		self.receiver = XPlaneReceiver(xp_host=hostname, xp_port=hostport, local_port=hostport)
		self.receiver.setCallback("sim/cockpit/radios/nav1_freq_hz", self.setValue)
		self.receiver.setCallback("sim/cockpit/radios/adf1_freq_hz", self.setValue)
		self.receiver.setCallback("sim/cockpit/radios/nav2_freq_hz", self.setValue)
		self.receiver.setCallback("sim/cockpit/radios/adf2_freq_hz", self.setValue)
		self.receiver.setCallback("sim/cockpit/radios/com1_freq_hz", self.setValue)
		self.receiver.setCallback("sim/cockpit/radios/com2_freq_hz", self.setValue)
		self.receiver.setCallback("sim/cockpit/radios/nav1_stdby_freq_hz", self.setValue)
		self.receiver.setCallback("sim/cockpit/radios/adf1_stdby_freq_hz", self.setValue)
		self.receiver.setCallback("sim/cockpit/radios/nav2_stdby_freq_hz", self.setValue)
		self.receiver.setCallback("sim/cockpit/radios/adf2_stdby_freq_hz", self.setValue)
		self.receiver.setCallback("sim/cockpit/radios/com1_stdby_freq_hz", self.setValue)
		self.receiver.setCallback("sim/cockpit/radios/com2_stdby_freq_hz", self.setValue)
		self.receiver.setCallback("sim/cockpit/radios/nav_com_adf_mode", self.setModeValue)
		self.receiver.setCallback("sim/cockpit/radios/nav_type", self.setModeValue)
		self.receiver.setCallback("sim/cockpit/electrical/instrument_brightness", self.setBrightness)
		self.receiver.setCallback("sim/cockpit2/electrical/panel_brightness_ratio", self.setBrightness)
		self.receiver.setCallback("sim/cockpit2/switches/panel_brightness_ratio", self.setBrightness)
		self.receiver.setCallback("sim/cockpit2/electrical/instrument_brightness_ratio", self.setBrightness)
		self.receiver.setCallback("sim/cockpit2/switches/instrument_brightness_ratio", self.setBrightness)
		self.receiver.start()

	def stopReceiver(self):
		self.receiver.stop()

	def getStandbyFrequencyKey(self):
		if self.Mode == self.MODE_NAV1:
			key = "sim/cockpit/radios/nav1_stdby_freq_hz"
		elif self.Mode == self.MODE_NAV2:
			key = "sim/cockpit/radios/nav2_stdby_freq_hz"
		elif self.Mode == self.MODE_ADF1:
			key = "sim/cockpit/radios/adf1_stdby_freq_hz"
		elif self.Mode == self.MODE_ADF2:
			key = "sim/cockpit/radios/adf2_stdby_freq_hz"
		elif self.Mode == self.MODE_COM1:
			key = "sim/cockpit/radios/com1_stdby_freq_hz"
		elif self.Mode == self.MODE_COM2:
			key = "sim/cockpit/radios/com2_stdby_freq_hz"
		return key

	def getActiveFrequencyKey(self):
		if self.Mode == self.MODE_NAV1:
			key = "sim/cockpit/radios/nav1_freq_hz"
		elif self.Mode == self.MODE_NAV2:
			key = "sim/cockpit/radios/nav2_freq_hz"
		elif self.Mode == self.MODE_ADF1:
			key = "sim/cockpit/radios/adf1_freq_hz"
			incr = -.5
		elif self.Mode == self.MODE_ADF2:
			key = "sim/cockpit/radios/adf2_freq_hz"
			incr = -.5
		elif self.Mode == self.MODE_COM1:
			key = "sim/cockpit/radios/com1_freq_hz"
		elif self.Mode == self.MODE_COM2:
			key = "sim/cockpit/radios/com2_freq_hz"
		return key

	def getStandbyFrequency(self):
		return self.variables[self.getStandbyFrequencyKey()]

	def setStandbyFrequency(self, freq):
		self.variables[self.getStandbyFrequencyKey()] = freq

	def getActiveFrequency(self):
		return self.variables[self.getActiveFrequencyKey()]

	def setActiveFrequency(self, freq):
		self.variables[self.getActiveFrequencyKey()] = freq

	def onEncoderLeft(self):
		# Decrement the frequency
		incr = -5
		maxfreq = 11800
		minfreq = 10800
		if self.Mode == self.MODE_NAV1:
			key = "sim/cockpit/radios/nav1_stdby_freq_hz"
		elif self.Mode == self.MODE_NAV2:
			key = "sim/cockpit/radios/nav2_stdby_freq_hz"
		elif self.Mode == self.MODE_ADF1:
			key = "sim/cockpit/radios/adf1_stdby_freq_hz"
			incr = -.5
		elif self.Mode == self.MODE_ADF2:
			key = "sim/cockpit/radios/adf2_stdby_freq_hz"
			incr = -.5
		elif self.Mode == self.MODE_COM1:
			key = "sim/cockpit/radios/com1_stdby_freq_hz"
		elif self.Mode == self.MODE_COM2:
			key = "sim/cockpit/radios/com2_stdby_freq_hz"
		freq = self.variables[key] + incr
		if freq < minfreq:
			freq = maxfreq
		elif freq > maxfreq:
			freq = minfreq
		print ("*** New value {} is {}".format(key, freq))
		self.variables[key] = freq
		if self.receiver != 0:
			self.receiver.sendValue(key, freq)

	def onEncoderRight(self):
		# Increment the frequency
		incr = 5
		maxfreq = 11800
		minfreq = 10800
		if self.Mode == self.MODE_NAV1:
			key = "sim/cockpit/radios/nav1_stdby_freq_hz"
		elif self.Mode == self.MODE_NAV2:
			key = "sim/cockpit/radios/nav2_stdby_freq_hz"
		elif self.Mode == self.MODE_ADF1:
			key = "sim/cockpit/radios/adf1_stdby_freq_hz"
			incr = .5
		elif self.Mode == self.MODE_ADF2:
			key = "sim/cockpit/radios/adf2_stdby_freq_hz"
			incr = .5
		elif self.Mode == self.MODE_COM1:
			key = "sim/cockpit/radios/com1_stdby_freq_hz"
		elif self.Mode == self.MODE_COM2:
			key = "sim/cockpit/radios/com2_stdby_freq_hz"
		freq = self.variables[key] + incr
		if freq < minfreq:
			freq = maxfreq
		elif freq > maxfreq:
			freq = minfreq
		print ("*** New value {} is {}".format(key, freq))
		self.variables[key] = freq
		if self.receiver != 0:
			self.receiver.sendValue(key, freq)

	def setBrightness(self, key, value):
		if key == "sim/cockpit/electrical/instrument_brightness":
			print ("New Brightness Value received {}".format(value))

	# this callback function will be called by the receiver upon receiption of a new frequency value
	def setValue(self, key, value):
		if key in self.variables.keys():
			self.variables[key] = value
			self.setMode(self.Mode)
			return True
		return False

	# this callback function will be called by the receiver upon receipton of a mode change
	def setModeValue(self, key, value):
		if key == "sim/cockpit/radios/nav_com_adf_mode":
			self.setMode(value)
		elif key == "sim/cockpit/radios/nav_type":
			print ("Received a new NAV_TYPE {}".format(value))

	# this function will update the mode LEDs as well as respective frequency displays
	def setMode(self, mode):
		print ("Mode is now %d" % mode)
		if mode == self.MODE_NAV1:
			self.display.setActiveFrequency(self.variables["sim/cockpit/radios/nav1_freq_hz"]/100)
			self.display.setStbyFrequency(self.variables["sim/cockpit/radios/nav1_stdby_freq_hz"] / 100)
			self.display.selectActiveMode(Display.NAV)
		elif mode == self.MODE_NAV2:
			self.display.setActiveFrequency(self.variables["sim/cockpit/radios/nav2_freq_hz"] / 100)
			self.display.setStbyFrequency(self.variables["sim/cockpit/radios/nav2_stdby_freq_hz"] / 100)
			self.display.selectActiveMode(Display.VOR)
		elif mode == self.MODE_COM1:
			self.display.setActiveFrequency(self.variables["sim/cockpit/radios/com1_freq_hz"] / 100)
			self.display.setStbyFrequency(self.variables["sim/cockpit/radios/com1_stdby_freq_hz"] / 100)
			self.display.selectStbyNavMode(Display.VHF1)
		elif mode == self.MODE_COM2:
			self.display.setActiveFrequency(self.variables["sim/cockpit/radios/com2_freq_hz"] / 100)
			self.display.setStbyFrequency(self.variables["sim/cockpit/radios/com2_stdby_freq_hz"] / 100)
			self.display.selectStbyNavMode(Display.VHF2)
		elif mode == self.MODE_ADF1:
			self.display.setActiveFrequency(self.variables["sim/cockpit/radios/adf1_freq_hz"])
			self.display.setStbyFrequency(self.variables["sim/cockpit/radios/adf1_stdby_freq_hz"])
			self.display.selectActiveMode(Display.MLS)
		elif mode == self.MODE_ADF2:
			self.display.setActiveFrequency(self.variables["sim/cockpit/radios/adf2_freq_hz"])
			self.display.setStbyFrequency(self.variables["sim/cockpit/radios/adf2_stdby_freq_hz"])
			self.display.selectActiveMode(Display.ADF)
		else:
			self.display.clearActiveFrequency()
			self.display.clearStbyFrequency()
			self.display.selectActiveMode(Display.CLR)
			self.display.selectStbyNavMode(Display.CLR)

	def stop(self):
		self.keyboard.stop()
		self.receiver.stop()
		print ("*** Radio terminating")

