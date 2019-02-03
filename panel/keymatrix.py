import RPi.GPIO as GPIO
import time
import threading

# mapping info
BTN_NAV = 0x32
BTN_VOR = 0x22
BTN_ILS = 0x02
BTN_MLS = 0x12

BTN_HF1 = 0x31
BTN_SEL = 0x21
BTN_HF2 = 0x01
BTN_AM  = 0x11

BTN_VHF1= 0x30
BTN_VHF2= 0x20
BTN_VHF3= 0x00
BTN_XCHG= 0x10

BTN_ADF = 0x03
BTN_BFO = 0x13

class Keyboard(threading.Thread):

	def __init__(self, cols, rows):
		threading.Thread.__init__(self)
		self.keys = [[0 for x in range(len(cols))] for y in range(len(rows))]
		# initialize the GPIO
		GPIO.setmode(GPIO.BCM)
		for c in cols:
			GPIO.setup(c, GPIO.OUT)
			GPIO.output(c, GPIO.HIGH)

		for r in rows:
			GPIO.setup(r, GPIO.IN, pull_up_down=GPIO.PUD_UP)

		self.cols = cols
		self.rows = rows
		self.col = len(cols)-1
		self.maxcol = self.col+1

		self.active = True

	def updateStatus(self, col, rows):
		for idx, r in enumerate(rows):
			if self.keys[col][idx] != r:
				self.keys[col][idx] = r
				kk = (col << 4) + idx
				if r == GPIO.LOW:
					print ("Key %02x was pressed" % kk)
				else:
					print ("Key %02x was released" % kk)



	def run(self):
		while self.active == True:
			# deactivate prev column
			GPIO.output(self.cols[self.col], GPIO.HIGH)
			self.col = self.col + 1
			if self.col > self.maxcol-1:
				self.col = 0
			GPIO.output(self.cols[self.col], GPIO.LOW)
			# wait shortly
			time.sleep(0.040)
			# read status
			rr = []
			for r in self.rows:
				rr.append( GPIO.input(r) )

			self.updateStatus(self.col, rr)

	def stop(self):
		self.active = False



