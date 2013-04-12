import socket
import select

network_timeout_start = -1.0 # Timeout in seconds to wait for the start of a message
network_timeout_delay = 1.0 # Maximum time between two characters being received

class NetworkPlayer(Player):
	def __init__(self, colour, network, player):
		Player.__init__(self, "@network:"+str(network.address), colour) 
		self.player = player
		self.network = network
		
	def __str__(self):
		return "NetworkPlayer<"+str(self.colour)+","+str(self.player)+">"
		
	def select(self):
		debug(str(self) + " select called")
		if self.player != None:
			s = self.player.select()
			self.send_message(str(s[0]) + " " + str(s[1]))
		else:
			s = map(int, self.get_response().split(" "))
			for p in game.players:
				if p != self and isinstance(p, NetworkPlayer) and p.player == None:
					p.network.send_message(str(s[0]) + " " + str(s[1]))
		return s
	
	def send_message(self, message):
		debug(str(self) + " send_message(\""+str(message)+"\") called")
		self.network.send_message(message)
		
	def get_response(self):
		debug(str(self) + " get_response() called")
		s = self.network.get_response()
		debug(str(self) + " get_response() returns \""+str(s)+"\"")
		return s
			
			
	def get_move(self):
		debug(str(self) + " get_move called")
		if self.player != None:
			s = self.player.get_move()
			self.send_message(str(s[0]) + " " + str(s[1]))
		else:
			s = map(int, self.get_response().split(" "))
			for p in game.players:
				if p != self and isinstance(p, NetworkPlayer) and p.player == None:
					p.network.send_message(str(s[0]) + " " + str(s[1]))
		return s
	
	def update(self, result):
		debug(str(self) + " update(\""+str(result)+"\") called")
		if self.network.server == True:
			if self.player == None:
				self.send_message(result)
		elif self.player != None:
			result = self.get_response()
			self.board.update(result, deselect=False)
		
		
		
		if self.player != None:
			result = self.player.update(result)
			
		return result
		
		
	
	def base_player(self):
		if self.player == None:
			return self
		else:
			return self.player.base_player()
		
	def quit(self, result):
		pass

class Network():
	def __init__(self, address = (None,4562)):
		self.socket = socket.socket()
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		#self.socket.setblocking(0)
		self.address = address
		self.server = (address[0] == None)
		
		
		self.connected = False
			
	def connect(self):	
		debug(str(self) + "Tries to connect")
		self.connected = True
		if self.address[0] == None:
			self.host = "0.0.0.0" #socket.gethostname() # Breaks things???
			self.socket.bind((self.host, self.address[1]))
			self.socket.listen(5)	

			self.src, self.actual_address = self.socket.accept()
			
			self.src.send("ok\n")
			s = self.get_response()
			if s == "QUIT":
				self.src.close()
				return
			elif s != "ok":
				self.src.close()
				self.__init__(colour, (self.address[0], int(s)), baseplayer)
				return
			
		else:
			time.sleep(0.3)
			self.socket.connect(self.address)
			self.src = self.socket
			self.src.send("ok\n")
			s = self.get_response()
			if s == "QUIT":
				self.src.close()
				return
			elif s != "ok":
				self.src.close()
				self.__init__(colour, (self.address[0], int(s)), baseplayer)
				return
			

		
	def __str__(self):
		return "@network:"+str(self.address)

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
		
		

		
