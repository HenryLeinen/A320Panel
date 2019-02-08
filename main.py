from panel.beacon import XPlaneBeaconListener
from panel.radio import Radio
import time




print ("Starting Radio class")
radio = Radio()

def xplaneDetectChange(stat, host):
	print ("Callback function ! Stat is %s" % stat )
	if stat == XPlaneBeaconListener.LISTENING:
		(hostname, hostport) = host
		print ("x-plane host found : %s" % hostname)
		radio.startReceiver(hostname, hostport)
	else:
		print ("x-plane signal lost ")
		radio.stopReceiver()

print ("Starting Beacon-finder")
beacon = XPlaneBeaconListener()
beacon.registerChangeEvent(xplaneDetectChange)
beacon.start()


cont = True

while cont:
    try:
		cont = True
		time.sleep(1)
    except KeyboardInterrupt:
		print ("quitting...")
		cont = False

radio.stop()
beacon.stop()
print ("Thread terminated !")


