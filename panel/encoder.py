import time
import RPi.GPIO as GPIO


class EventManager:
	class Event:
		def __init__(self, functions):
			if type(functions) is not list:
				raise ValueError("function parameter shall be a list !")
			self.functions = functions

		def __iadd__(self, func):
			self.functions.append(func)
			return self

		def __isub__(self, func):
			self.functions.remove(func)
			return self

		def __call__(self, *args, **kvargs):
			for func in self.functions : func(*args, **kvargs)
	@classmethod
	def addEvent(cls,**kvargs):
		"""
		addEvent( event1 = [f1,f2,...], event2 = [g1,g2,...], ... )
		creates events using **kvargs to create any number of events. Each event recieves a list of functions,
		where every function in the list recieves the same parameters.

		Example:

		def hello(): print "Hello ",
		def world(): print "World"

		EventManager.addEvent( salute = [hello] )
		EventManager.salute += world

		EventManager.salute()

		Output:
		Hello World
		"""
		for key in kvargs.keys():
			if type(kvargs[key]) is not list:
				raise ValueError("value has to be a list")
			else:
				kvargs[key] = cls.Event(kvargs[key])

		cls.__dict__.update(kvargs)


class Encoder:

	def __init__(self, CLKPIN, DIRPIN, BTNPIN):
		self.ENC_A = CLKPIN
		self.ENC_B = DIRPIN
		self.ENC_BUTTON = BTNPIN
		# set either BOARD or BCM mode.
		GPIO.setmode(GPIO.BCM)
		# set the three encoder pins as INPUTS with PULL up
		GPIO.setup(self.ENC_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.ENC_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.ENC_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(self.ENC_A, GPIO.BOTH, callback=self.pinChanged, bouncetime=20)
		#GPIO.add_event_detect(ENC_B, GPIO.BOTH, callback=pin_low, bouncetime=300)
		GPIO.add_event_detect(self.ENC_BUTTON, GPIO.BOTH, callback=self.pinChanged, bouncetime=200)

	def registerLeftEvent(self, func):
		EventManager.addEvent( onLeft = [func])

	def registerRightEvent(self, func):
		EventManager.addEvent( onRight = [func])

	def registerButtonPressedEvent(self, func):
		EventManager.addEvent( onBtnPressed = [func])

	def registerButtonReleasedEvent(self, func):
		EventManager.addEvent( onBtnReleased = [func])

	def pinChanged(self, channel):
		Clk = GPIO.input(self.ENC_A)
		Dir = GPIO.input(self.ENC_B)
		Btn = GPIO.input(self.ENC_BUTTON)
		if channel == self.ENC_A:
			if (Clk == GPIO.LOW and Dir == GPIO.HIGH) or (Clk == GPIO.HIGH and Dir == GPIO.LOW):
				# Detected a right turn
				EventManager.onRight()
			else :
				# Detected a left turn
				EventManager.onLeft()
		elif channel == self.ENC_BUTTON:
			if Btn == GPIO.LOW:
				# Detected a button press
				if EventManager.onBtnPressed:
					EventManager.onBtnPressed()
			else:
				# Detected a button release
				if EventManager.onBtnReleased:
					EventManager.onBtnReleased()




