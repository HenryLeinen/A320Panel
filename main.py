from panel.beacon import XPlaneBeaconListener
from panel.panel import XPlaneReceiver
from panel.max7219 import Lcd

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


