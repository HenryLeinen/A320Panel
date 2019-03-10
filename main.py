from panel.radio import Radio
import time




print ("Starting Radio class")
radio = Radio()

cont = True

while cont == True:
	try:
		cont = True
		time.sleep(1)
	except KeyboardInterrupt:
		print ("quitting...")
		cont = False


radio.stop()
print ("Thread terminated !")


