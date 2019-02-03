from panel.beacon import XPlaneBeaconListener
from panel.xplane import XPlaneReceiver
from panel.max7219 import Lcd
from panel.display import Display


print ("Setup display")
display = Display()

print ("Locating Beacon")
x = XPlaneBeaconListener()
(host, port) = x.listen()
print ("X-Plane deteced on %s" % host)

receiver = XPlaneReceiver(xp_host=host, xp_port=port, local_port=port)
receiver.start()
cont = True

while cont:
    try:
        cont = True
    except KeyboardInterrupt:
        print ("quitting...")
        cont = False

receiver.stop()
print ("Waiting for thread termination")
#receiver.join()
print ("Thread terminated !")


