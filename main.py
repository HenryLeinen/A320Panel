from panel.beacon import XPlaneBeaconListener
from panel.xplane import XPlaneReceiver
from panel.max7219 import Lcd
from panel.display import Display
from panel.encoder import Encoder
from panel.keymatrix import Keyboard




def onEncoderLeft():
	global freq
	freq = freq - 0.125
	if freq < 108.0:
		freq = 122.0
	print ("Left turn: New stby freq: %3.3f" % freq)

def onEncoderRight():
	global freq
	freq = freq + 0.125
	if freq > 122.0:
		freq = 108.0
	print ("Right turn: New stby freq: %3.3f" % freq)




print ("Setup display")
display = Display()

print ("Setup Keyboard")
keyboard = Keyboard( [0,5,6,13], [4,3,2,19])
keyboard.start()

print ("Setup encoder system")
freq = 108.0
encoder = Encoder(17, 27, 22)
encoder.registerLeftEvent(onEncoderLeft)
encoder.registerRightEvent(onEncoderRight)

def xplaneDetectChange(stat, host):
	global receiver
	print ("Callback function ! Stat is %s" % stat )
	if stat == XPlaneBeaconListener.LISTENING:
		(hostname, hostport) = host
		print ("x-plane host found : %s" % hostname)
		receiver = XPlaneReceiver(xp_host=hostname, xp_port=hostport, local_port=hostport)
		receiver.start()
	else:
		print ("x-plane signal lost ")
		if receiver != 0:
			receiver.stop()
			receiver = 0

print ("Staring Beacon-finder")
x = XPlaneBeaconListener()
x.registerChangeEvent(xplaneDetectChange)
x.start()

receiver = 0

cont = True

while cont:
    try:
        cont = True
    except KeyboardInterrupt:
        print ("quitting...")
        cont = False

keyboard.stop()
x.stop()
if receiver != 0:
	receiver.stop()
print ("Waiting for thread termination")
#receiver.join()
print ("Thread terminated !")


