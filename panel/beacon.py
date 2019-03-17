import socket
import threading
import struct

# THis class will listen for the beacon, which is broadcasted from each x-plane instance on the local network
class XPlaneBeaconListener(threading.Thread):
	SEARCHING = 1
	LISTENING = 2
	def __init__(self, dbg=0):
		self.dbg=dbg
		#i initialize threading
		threading.Thread.__init__(self)
		self.active = True
		# create a datagram socket
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# make sure the socketaddress can be shared with others (otherwise we would block)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self.sock.settimeout(3.0)

		# x-plane send the beacon via a multicast, the address is 239.255.1.1
		group = socket.inet_aton("239.255.1.1")
		mreq = struct.pack('4sL', group, socket.INADDR_ANY)
		self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
		self.sock.bind (("", 49707))
		self.state = self.SEARCHING
		self.callback = []
		self.host = ("",0)

	def changeState(self, newstate):
		if newstate != self.state:
			# change of state detected. Call callback function if existing
			self.state = newstate
			for func in self.callback:
				func(self.state, self.host)
			return True
		else:
			return False

	def registerChangeEvent(self, cbk):
		self.callback.append(cbk)

	def run(self):
		while self.active == True:
			try:
				msg, addr = self.sock.recvfrom(1024)

				if msg[0:5] != b"BECN\x00":
					print ("Unknown message received !")
				else:
					if self.dbg >=1:
						print ("Beacon received, checking the data provided")
					(maj, min, host, ver, role, port) = struct.unpack("<BBiiIH", msg[5:21])
					sdta = msg[21:].split(b'\0')
					host_name=sdta[0]
					self.host = (host_name, port)
					self.changeState(self.LISTENING)
			except socket.timeout:
				self.changeState(self.SEARCHING)
		self.sock.close()

	def stop(self):
		self.active = False
