from panel.config import config
from panel.beacon import XPlaneBeaconListener
import socket
import struct
import sys
import threading

class xplane(threading.Thread):

	def __init__(self, cnf, dbg=0):
		threading.Thread.__init__(self)
		self.active = True
		self.debug = dbg
		# Initialize the config file parser
		self.cfg = cnf
		# start listening for the X-Plane beacon, which tells us where x-plane is currently running
		self.beacon = XPlaneBeaconListener()
		self.beacon.registerChangeEvent(self.xPlaneHostChange)
		self.beacon.start()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.sock.settimeout(3.0)
		self.UDP_XPL = ("localhost", 49009)
		self.UDP_LCL = ("", 49009)
		self.sock.bind(self.UDP_LCL)
		# prepare all internal lookup tables for datarefs and callbacks
		self.datarefs = {}
		self.datarefidx = 0
		self.xplaneValues = {}
		self.callbacks = {}

	# EXPORTED FUNCTION
	# This function is used by the user of this class and registers a callback function for a particular variable.
	# The variable is a logical variable name, which will internally be translated into an xplane variable using a lookup table
	def setCallback(self, var, cbk):
		# lookup the dataref value which is related to the given variable
		if var in self.cfg.getRequests().keys():
			dataref = self.cfg.getRequests()[var]
			if self.debug >=2:
				print ("Setting callback for variable %s"%dataref)
			self.callbacks[dataref] = cbk
		else:
			if self.debug >=1:
				print("Callback for variable %s cannot be set."% var)

	# INTERNAL FUNCTION
	# This function will reinterpret a value received from x-plane into the related logical value which is relevant for the user
	def _reinterpret(self, var, val):
		# get the type
		t_type = self.cfg.getVariableItem(var,"type")
		if t_type == "bool":
			if val == 1.0:
				return True
			else:
				return False
		elif t_type == "float":
			return float(val)
		elif t_type == "enum":
			# get the name of the map
			t_map = self.cfg.getVariableItem(var,"map")
			t_val_idx = list(self.cfg.getMap(t_map).values()).index(str(val))
			return list(self.cfg.getMap(t_map).keys())[t_val_idx]
		elif t_type == "linear":
			t_offs = float(self.cfg.getVariableItem(var,"offset"))
			t_slp  = float(self.cfg.getVariableItem(var,"slope"))
			# y = offs + m*x   ==> x = (y-offs)/m
			t_val = (float(val)-t_offs) / t_slp
			t_min = float(self.cfg.getVariableItem(var, "range_in_min"))
			t_max = float(self.cfg.getVariableItem(var, "range_in_max"))
			if t_val < t_min:
				t_val = t_min
			elif t_val > t_max:
				t_val = t_max
			return t_val
		else:
			print ("Unknown error !!!!!!!!")

	def xPlaneHostChange(self, stat, host):
		if stat == XPlaneBeaconListener.LISTENING:
			(hostname,hostport) = host
			if self.debug >=1:
				print ("X-Plane instance found on %s:%d", hostname, hostport)
			# start the receiver
			self.UDP_XPL = (socket.gethostbyname(hostname),hostport)
			self.UDP_LCL = ("localhost",hostport)
			self.startReceiver()
		else:
			# stop the receiver
			if self.debug >= 1:
				print ("X-Plane signal lost !")
			self.UDP_XPL = ("localhost", 49009)
			self.stopReceiver()

	# EXPORTED FUNCTION
	# This function must be used to stop receiving from x-plane. It also stops the beacon receiver and closes the socket in order to terminate.
	def stop(self):
		self.active = False
		# stop the beacon
		self.beacon.stop()
		# shutdown the socket
		self.sock.close()
		# stop the receiver
		self.stopReceiver()

	# INTERNAL FUNCTION
	# Send a dataref change to x-plane
	def _sendValue(self, dataref, value):
		cmd = b"DREF\x00"
		string = dataref.encode('utf-8')
		string+= '\x00'
		message = struct.pack("<5sf500s", cmd, value, string)
		assert(len(message)==509)
		if self.debug >= 2:
			print ('Sending to {}:{} dataref {}={}'.format(self.UDP_XPL[0], self.UDP_XPL[1], dataref, value))
		self.sock.sendto(message, self.UDP_XPL)

	# EXPORTED FUNCTION
	# This function sends a value to x-plane. It uses the configuration structure to find out how to interpret the 
	# value to send
	def setValue(self, var, value):
		# look up the item in the configuration structure
		if var in self.cfg.getVariables().keys():
			if self.debug >=2:
				print ("Setting item %s to value %s" %(var, str(value)))
			# item does exist, so lookup the dataref and the type
			# get the type
			t_type = self.cfg.getVariableType(var)
			if t_type == "bool":
				if value > 0:
					t_val = 1.0
				else:
					t_val = 0.0
				if self.debug >=2:
					print ("Now sending {} to {}".format(t_val, self.cfg.getVariables()[var]))
				self._sendValue(self.cfg.getVariables()[var], float(t_val))
			elif t_type == "float":
				if self.debug >=2:
					print ("Now sending {} to {}".format(value, self.cfg.getVariables()[var]))
				self._sendValue(self.cfg.getVariables()[var], float(value))
			elif t_type == "enum":
				# get the name of the map
				t_map = self.cfg.getVariableItem(var, "map")
				t_val = self.cfg.getMap(t_map)[value]
				self._sendValue(self.cfg.getVariables()[var], float(t_val))
			elif t_type == "linear":
				# get min, max values against which we need to clip the input
				t_min = float(self.cfg.getVariableItem(var, "range_in_min"))
				t_max = float(self.cfg.getVariableItem(var, "range_in_max"))
				if float(value) < t_min:
					value = t_min
				elif float(value) > t_max:
					value = t_max
				# get the offset and the slope to calculate the new value
				t_offs = float(self.cfg.getVariableItem(var, "offset"))
				t_slp  = float(self.cfg.getVariableItem(var, "slope"))
				t_val = t_offs + t_slp*float(value)
				if self.debug >=2:
					print ("Now sending {} to {}".format(t_val, self.cfg.getVariables()[var]))
				self._sendValue(self.cfg.getVariables()[var], float(t_val))
			else:
				print ("Invalid mapping table !!!")
		else:
			print ('******* setValue: Invalid item {}*******'.format(var))

	# INTERNAL FUNCTION
	# This function will send a dataref request to x-plane. The update frequency is optional and defaults to 1 per second
	def _request(self, dataref, freq=None):
		if freq == None:
			freq = 1
		# check whether or not this has already been requested
		if dataref in self.datarefs.values():
			# yes, it's there so get the index
			idx = list(self.datarefs.keys()) [list(self.datarefs.values()).index(dataref)]
			# check if dataref also exists in the xplaneValues
			if dataref in self.xplaneValues.keys():
				del self.xplaneValues[dataref]
			del self.datarefs[idx]
		else:
			idx = self.datarefidx
			self.datarefs[self.datarefidx] = dataref
			self.datarefidx += 1
			self.xplaneValues[dataref] = 0
		cmd = b"RREF\x00"
		string = dataref.encode('utf-8') + '\x00'
		if self.debug >=1:
			print ("Requesting dataref %s using index %d" % (dataref, idx))
		message = struct.pack("<5sii400s", cmd, freq, idx, string)
		assert(len(message)==413)
		if self.debug>=2:
			print ('Sending to {}:{} dataref {}={}'.format(self.UDP_XPL[0], self.UDP_XPL[1], freq, dataref))
		self.sock.sendto(message, self.UDP_XPL)

	# INTERNAL FUNCTION
	# This function will subscribe to all datarefs given in the configuration file listed under the 'Requests' section.
	def _subscribe(self):
		for var in list(self.cfg.getRequests().keys()):
			self._request(self.cfg.getRequests()[var])

	# EXTERNAL FUNCTION
	# This function will initiate the receiver function by resubscribing to the dataref values from the config file.
	def startReceiver(self):
		# Subscribe to the datarefs
		self._subscribe()

	# EXTERNAL FUNCTION
	# This function currently does nothing meaningful
	def stopReceiver(self):
		pass

	# INTERNAL FUNCTION
	# This function will parse a list of received datarefs for changes. If changes are found, it will inform the user by calling the respective callback function
	# which has been registered previously be the user of this class using the external function <setCallback>
	def _parse(self, retvalues):
		for idx in retvalues:		# iterate through the returned values using the 'dataref' value
			if idx in self.xplaneValues.keys():
				orgval = self.xplaneValues[idx]
				newval = retvalues[idx]
				if orgval != newval:
					if self.debug >=1:
						print ("Value %s has changed from %s to %s." %(str(idx).strip(b'\x00'), str(orgval), str(newval)))
					# trigger change notification
					self.xplaneValues[idx] = newval
					# call callback function if existing
					if idx in self.callbacks.keys():
						if self.debug >=1:
							print ("Calling callback for %s" % idx.strip('\x00'))
						v1 = list(self.cfg.getRequests().values()).index(idx)
						v2 = list(self.cfg.getRequests().keys())[v1]
						newval_int = self._reinterpret(v2, newval)		# revers interpret the x-plane value into the logical value known to the calling app
						if self.debug >=3:
							print ("New value is %d, converting %s"%(newval, newval_int))
						self.callbacks[idx](v2, newval_int)
					else:
						if self.debug >=1:
							print ("No callback for %s" % idx)
				else:
					#print ("Value did not change")
					pass
			else:
				self.xplaneValues[idx] = newval
				print ("################ Unknown dataref received %s" % idx)


	def run(self):
		if self.debug >=1:
			print ("Starting receiver loop")
		while self.active == True:
			try:
				# receive a packet
				data = self.sock.recv(1024)
				# temporary collection of values
				retvalues = {}
				# read the header of the message
				header = data[0:4]
				if header == b"RREF":
					# we get 8 bytes for each dataref
					# an integer for the idx and the float value
					values = data[5:]
					num_values = int(len(values)/8)

					# extract all received values
					for i in range(0, num_values):
						# extract each individual value from the stream
						singledata = values[i*8:(i+1)*8]
						(idx, fval) = struct.unpack("<if", singledata)
						#print ("Item with index %d found" %idx)
						if idx in self.datarefs.keys():
							# retvalues is a map of 'dataref': float_value pairs
							retvalues[self.datarefs[idx]] = fval
					# parse the values to find out what changes we received
					self._parse(retvalues)
				elif header == b"RPOS":
					print ("Position information rececived !")
				elif header == b"DATA":
					print ("DATA block received !")
				else:
					print ("Unknown packet received !", data[0:4])
			except socket.timeout:
				if self.debug >=1:
					print ("*********PING********")
				pass
			except socket.error:
				print ("Socket error !")
				pass
			except :
				print ("Bullshit exception")
				raise
		print ("Terminating receiver loop")
		self.sock.close()

