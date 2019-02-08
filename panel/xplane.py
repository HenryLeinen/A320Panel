import socket
import threading
import struct
import sys

class XPlaneReceiver(threading.Thread):

	def __init__(self, xp_host='localhost', xp_port=49009, local_port=49009):
		threading.Thread.__init__(self)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.sock.settimeout(3.0)

		self.active = True
		self.datarefs = {}		# key = index, value = dataref
		self.datarefidx = 0		# first index is 0

		if xp_port < 0 or xp_port > 65535:
			raise ValueError("Invalid port <xp_port>" + str(xp_port))
		if local_port < 0 or local_port > 65535:
			raise ValueError("Invalid port <port>" + str(local_port))

		self.UDP_XPL = (socket.gethostbyname(xp_host), xp_port)
		self.UDP_LOCAL = ("", local_port)

		self.xplaneValues = {}

		self.callbacks = {}	# Dictionary stores for each key a callback function

	def request(self, dataref, freq=None):
		# check if frequency is deault (not provided)
		if freq == None:
			freq = 1		# default frequency is 1 message per second

		# check whether dataref is already requested
		if dataref in self.datarefs.values():
			#get the index
			idx = list(self.datarefs.keys()) [list(self.datarefs.values()).index(dataref)]
			# check if dataref also exists in the xplaneValues
			if dataref in self.xplaneValues.keys():
				del self.xplaneValues[datarefs]
			del self.datarefs[idx]
		else:
			idx = self.datarefidx
			self.datarefs[self.datarefidx] = dataref
			self.datarefidx += 1
			self.xplaneValues[dataref] = 0
		cmd = b"RREF\x00"
		string = dataref.encode()
		message = struct.pack("<5sii400s", cmd, freq, idx, string)
		print ("Requesting " + dataref + " with index " + str(idx) + " from " , self.UDP_XPL)
		assert(len(message)==413)
		self.sock.sendto(message, self.UDP_XPL)

	def sendValue(self, dataref, value):
		cmd = b"DREF\x00"
		string = dataref.encode()
		message = struct.pack("<5sf500s", cmd, value, string)
		print ("Sending " + dataref + " with value " + str(value))
		assert(len(message)==509)
		self.sock.sendto(message, self.UDP_XPL)

	def do_request(self):
		self.request("sim/cockpit/radios/nav1_freq_hz", 10)
		self.request("sim/cockpit/radios/nav2_freq_hz",2)
		self.request("sim/cockpit/radios/com1_freq_hz",2)
		self.request("sim/cockpit/radios/com2_freq_hz",2)
		self.request("sim/cockpit/radios/adf1_freq_hz",10)
		self.request("sim/cockpit/radios/adf2_freq_hz",10)
		self.request("sim/cockpit/radios/dme_freq_hz",10)
		self.request("sim/cockpit/radios/nav1_stdby_freq_hz")
		self.request("sim/cockpit/radios/nav2_stdby_freq_hz")
		self.request("sim/cockpit/radios/com1_stdby_freq_hz")
		self.request("sim/cockpit/radios/com2_stdby_freq_hz")
		self.request("sim/cockpit/radios/adf1_stdby_freq_hz")
		self.request("sim/cockpit/radios/adf2_stdby_freq_hz")
		self.request("sim/cockpit/radios/dme_stdby_freq_hz")

		# Buttons on the radio change the mode:
		# NAV1 = 0, NAV2 = 1, COM1 = 2, COM2 = 3, ADF1 = 4, ADF2 = 5
		self.request("sim/cockpit/radios/nav_com_adf_mode")

	def parse(self, retvalues):
		# task of this function is to inform about changes received

		try:
			for idx in retvalues:
				if idx in self.xplaneValues.keys():
					orgval = self.xplaneValues[idx]
					newval = retvalues[idx]
					if orgval !=newval:
						print ("Value " + idx + " has changed from " + str(orgval) + " to " + str(newval))
						# trigger change
						self.xplaneValues[idx] = newval
						# call callback function if one is configured
						if idx in self.callbacks.keys():
							print ("Calling callback for %s" %idx)
							self.callbacks[idx](idx, newval)
						else:
							print ("No callback for %s" %idx)
				else:
					self.xplaneValues[idx] = newval
				pass
		except Exception as e:
			print ("Exception caught %s" % str(e))

	def setCallback(self, var, cbk):
		# check if the variable is already registered
		self.callbacks[var] = cbk

	def run(self):
		print ("Binding to ", self.UDP_LOCAL)
		self.sock.bind(self.UDP_LOCAL)
		self.do_request()

		print ("Starting loop")
		while self.active == True:
			try:
				# receive packet
				data = self.sock.recv(1024)
				# this is a temporary collextion of the decoded values
				retvalues = {}
				# read the header RREF
				header = data[0:4]
				if header == b"RREF":
					# we get 8 bytes for each dataref sent:
					# an integer for he idx and the float value
					values = data[5:]
					num_values = int(len(values)/8)

					# extract all received values
					for i in range(0, num_values):
						# extract each individual value from the stream
						singledata = values[i*8:(i+1)*8]
						(idx, fval) = struct.unpack("<if", singledata)
						if idx in self.datarefs.keys():
							retvalues[self.datarefs[idx]] = fval
					# parse the values to find out what changes we received
					self.parse(retvalues)
				elif header == "RPOS":
					print ("Position information received !")
				elif header == "DATA":
					print ("DATA block received !")
				else:
					print ("Unknown packet received !", data[0:4])
			except socket.timeout:
				print ("Timeout on XPlaneReceiver")
				pass
			except socket.error:
				print ("Socket error ")
				pass
			except :
				print ("Bullshit exception")
				pass
		
		print ("WTF")
		self.sock.close()


	def stop(self):
		print ("*** xplaneReceiver terminating")
		self.active = False



