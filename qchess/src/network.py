import socket
import select

network_timeout_start = -1.0 # Timeout in seconds to wait for the start of a message
network_timeout_delay = 1.0 # Maximum time between two characters being received

class Network(Player):
	def __init__(self, colour, address = (None,4562), baseplayer = None):
		
		if baseplayer != None:
			name = baseplayer.name + " --> @network"
		else:
			name = "<-- @network"
		
		
				
		Player.__init__(self, name, colour)
		debug("Colour is " + str(self.colour))
		
		self.socket = socket.socket()
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.baseplayer = baseplayer
		#self.socket.setblocking(0)
		
		self.address = address
		self.server = (address[0] == None)

		if self.colour == "black":
			self.address = (self.address[0], self.address[1] + 1)
				
		debug(str(self) + ":"+str(self.address))
		
		self.board = None
			
			
	def connect(self):	
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
			

	def select(self):
		if self.baseplayer != None:
			s = self.baseplayer.select()
			self.send_message(str(s[0]) + " " + str(s[1]))
			return s
		return map(int,self.get_response().split(" "))
	
	def get_move(self):
		if self.baseplayer != None:
			s = self.baseplayer.get_move()
			self.send_message(str(s[0]) + " " + str(s[1]))
			return s
		return map(int,self.get_response().split(" "))
	
	def update(self, result):
		if self.baseplayer != None:
			result = self.baseplayer.update(result)
			self.send_message(result)
			return result
		if self.server:
			self.send_message(result)
		else:
			s = self.get_response()
			if self.board != None:
				self.board.update(s)
			
	def __str__(self):
		return "Network<"+str(self.colour)+","+str(self.baseplayer)+">:"+str(self.address)

	def get_response(self):
		debug(str(self) + " get_response called...")
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

		debug(str(self) + " get_response returns " + s.strip(" \r\n"))
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
		
		debug(str(self) + " send_message sent " + s)

	def check_quit(self, s):
		s = s.split(" ")
		if s[0] == "QUIT":
			with game.lock:
				game.final_result = " ".join(s[1:]) + " " + str(opponent(self.colour))
			game.stop()
			return True
			
	def quit(self, result):
		if self.baseplayer != None:
			self.send_message("QUIT")
			
		with game.lock:
			game.final_result = result
		game.stop()	




		
