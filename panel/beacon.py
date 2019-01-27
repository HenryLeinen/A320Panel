import socket
import threading
import struct

# THis class will listen for the beacon, which is broadcasted from each x-plane instance on the local network
class XPlaneBeaconListener():

	def __init__(self):
		# create a datagram socket
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# make sure the socketaddress can be shared with others (otherwise we would block)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

		# x-plane send the beacon via a multicast, the address is 239.255.1.1
		group = socket.inet_aton("239.255.1.1")
		mreq = struct.pack('4sL', group, socket.INADDR_ANY)
		self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
		self.sock.bind (("", 49707))


	def listen(self):
		while True:
			msg, addr = self.sock.recvfrom(1024)

			if msg[0:5] != b"BECN\x00":
				print ("Unknown message received !")
			else:
				print ("Beacon received, checking the data provided")
				(maj, min, host, ver, role, port) = struct.unpack("<BBiiIH", msg[5:21])
				sdta = msg[21:].split(b'\0')
				host_name=sdta[0]
				print ("Host detected ", host_name)
				print (" on port " , port,  " with version " , maj,  "." ,min, " Role:" ,role)
				return (host_name, port)
