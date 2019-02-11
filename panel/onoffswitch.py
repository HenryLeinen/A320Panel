import RPi.GPIO as GPIO



class OnOffSwitch:

    def __init__(self, pin, switch_callback):
        self.pin = pin
        self.callback = switch_callback
		# set either BOARD or BCM mode.
        GPIO.setmode(GPIO.BCM)
        # set the three encoder pins as INPUTS with PULL up
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=self.pinChanged, bouncetime=20)


    def pinChanged(self, channel):
        if channel == self.pin:
            if self.callback != 0:
                lvl = not GPIO.input(self.pin)
                self.callback(lvl)
                print ("*** OnOff Switch has been switched to " + str(lvl))

    def getState(self):
        if GPIO.input(self.pin) == GPIO.HIGH:
            return False
        return True