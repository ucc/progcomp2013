import socket
import select

network_timeout_start = -1.0 # Timeout in seconds to wait for the start of a message
network_timeout_delay = 1.0 # Maximum time between two characters being received

class Network():
	def __init__(self, colour, address = None):
		self.socket = socket.socket()
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		#self.socket.setblocking(0)
		
		self.server = (address == None)

		if colour == "white":
			self.port = 4562
		else:
			self.port = 4563

		self.src = None

	#	print str(self) + " listens on port " + str(self.port)

		if address == None:
			self.host = "0.0.0.0" #socket.gethostname() # Breaks things???
			self.socket.bind((self.host, self.port))
			self.socket.listen(5)	

			self.src, self.address = self.socket.accept()
			self.src.send("ok\n")
			if self.get_response() == "QUIT":
				self.src.close()
		else:
			self.host = address
			self.socket.connect((address, self.port))
			self.src = self.socket
			self.src.send("ok\n")
			if self.get_response() == "QUIT":
				self.src.close()
			self.address = (address, self.port)

	def get_response(self):
		# Timeout the start of the message (first character)
		if network_timeout_start > 0.0:
			ready = select.select([self.src], [], [], network_timeout_start)[0]
		else:
			ready = [self.src]
		if self.src in ready:
			s = self.src.recv(1)
		else:
			raise Exception("UNRESPONSIVE")


		while s[len(s)-1] != '\n':
			# Timeout on each character in the message
			if network_timeout_delay > 0.0:
				ready = select.select([self.src], [], [], network_timeout_delay)[0]
			else:
				ready = [self.src]
			if self.src in ready:
				s += self.src.recv(1) 
			else:
				raise Exception("UNRESPONSIVE")

		return s.strip(" \r\n")

	def send_message(self,s):
		if network_timeout_start > 0.0:
			ready = select.select([], [self.src], [], network_timeout_start)[1]
		else:
			ready = [self.src]

		if self.src in ready:
			self.src.send(s + "\n")
		else:
			raise Exception("UNRESPONSIVE")

	def check_quit(self, s):
		s = s.split(" ")
		if s[0] == "QUIT":
			with game.lock:
				game.final_result = " ".join(s[1:]) + " " + str(opponent(self.colour))
			game.stop()
			return True


		

class NetworkSender(Player,Network):
	def __init__(self, base_player, address = None):
		self.base_player = base_player
		Player.__init__(self, base_player.name, base_player.colour)

		self.address = address

	def connect(self):
		nAttempts=3
		for i in range(nAttempts):
			try:
				Network.__init__(self, self.colour, self.address)
				debug(str(self) +" connected to " + str(self.address))
				return
			except Exception, e:
				debug(str(self) +" attempt " + str(i) + ": " +  str(e.message))
				
		raise Exception("NETWORK - Can't connect to " + str(self.address))


	def select(self):
		[x,y] = self.base_player.select()
		choice = self.board.grid[x][y]
		s = str(x) + " " + str(y)
		#debug(str(self) + " sends: " + str(s))
		self.send_message(s)
		return [x,y]

	def get_move(self):
		[x,y] = self.base_player.get_move()
		s = str(x) + " " + str(y)
		#debug(str(self) + " sends: " + str(s))
		self.send_message(s)
		return [x,y]

	def update(self, s):
		
		self.base_player.update(s)
		if self.server == True:
			#debug(str(self) + " sends: " + str(s))
			self.send_message(s)
		return s
		
		s = s.split(" ")
		[x,y] = map(int, s[0:2])
		selected = self.board.grid[x][y]
		if selected != None and selected.colour == self.colour and len(s) > 2 and not "->" in s:
			s = " ".join(s[0:3])
			for i in range(2):
				if selected.types[i][0] != '?':
					s += " " + str(selected.types[i])
				else:
					s += " unknown"
			#debug(str(self) +" sending: " + str(s))
			self.send_message(s)
				

	def quit(self, final_result):
		self.base_player.quit(final_result)
		#self.src.send("QUIT " + str(final_result) + "\n")
		self.src.close()
		
	def __str__(self):
		s = "NetworkSender:"
		if self.server:
			s += "server"
		else:
			s += "client"
		s += ":"+str(self.address)
		return s


class NetworkReceiver(Player,Network):
	def __init__(self, colour, address=None):
		
		s = "@network"
		if address != None:
			s += ":"+str(address)
		Player.__init__(self, s, colour)

		self.address = address

		self.board = None


	def connect(self):
		nAttempts=3
		for i in range(nAttempts):
			try:
				Network.__init__(self, self.colour, self.address)
				debug(str(self) +" connected to " + str(self.address))
				return
			except Exception, e:
				debug(str(self) +" attempt " + str(i) + ": " +  str(e.message))
				
		raise Exception("NETWORK - Can't connect to " + str(self.address))
			
			

	def select(self):
		
		s = self.get_response()
		#debug(str(self) +".select reads: " + str(s))
		[x,y] = map(int,s.split(" "))
		if x == -1 and y == -1:
			#print str(self) + ".select quits the game"
			with game.lock:
				game.final_state = "network terminated " + self.colour
			game.stop()
		return [x,y]
	def get_move(self):
		s = self.get_response()
		#debug(str(self) +".get_move reads: " + str(s))
		[x,y] = map(int,s.split(" "))
		if x == -1 and y == -1:
			#print str(self) + ".get_move quits the game"
			with game.lock:
				game.final_state = "network terminated " + self.colour
			game.stop()
		return [x,y]

	def update(self, result):
		if self.server == True:
			return result
		s = self.get_response()
		#debug(str(self) + ".update reads: " + str(s))
		if not "->" in s.split(" "):
			self.board.update(s, sanity=False)
		return s
		

	def quit(self, final_result):
		self.src.close()
		
	def __str__(self):
		s = "NetworkReceiver:"
		if self.server:
			s += "server"
		else:
			s += "client"
		s += ":"+str(self.address)
		return s
	
