import socket
import select

network_timeout_start = -1.0 # Timeout in seconds to wait for the start of a message
network_timeout_delay = 1.0 # Maximum time between two characters being received

class Network():
	def __init__(self, colour, address = None):
		self.socket = socket.socket()
		#self.socket.setblocking(0)

		if colour == "white":
			self.port = 4562
		else:
			self.port = 4563

		self.src = None

	#	print str(self) + " listens on port " + str(self.port)

		if address == None:
			self.host = socket.gethostname()
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
		Network.__init__(self, self.base_player.colour, self.address)



	def select(self):
		[x,y] = self.base_player.select()
		choice = self.board.grid[x][y]
		s = str(x) + " " + str(y)
		#print str(self) + ".select sends " + s
		self.send_message(s)
		return [x,y]

	def get_move(self):
		[x,y] = self.base_player.get_move()
		s = str(x) + " " + str(y)
		#print str(self) + ".get_move sends " + s
		self.send_message(s)
		return [x,y]

	def update(self, s):
		self.base_player.update(s)
		s = s.split(" ")
		[x,y] = map(int, s[0:2])
		selected = self.board.grid[x][y]
		if selected != None and selected.colour == self.colour and len(s) > 2 and not "->" in s:
			s = " ".join(s[0:3])
			for i in range(2):
				if selected.types_revealed[i] == True:
					s += " " + str(selected.types[i])
				else:
					s += " unknown"
			#print str(self) + ".update sends " + s
			self.send_message(s)
				

	def quit(self, final_result):
		self.base_player.quit(final_result)
		#self.src.send("QUIT " + str(final_result) + "\n")
		self.src.close()

class NetworkReceiver(Player,Network):
	def __init__(self, colour, address=None):
		
		Player.__init__(self, address, colour)

		self.address = address

		self.board = None

	def connect(self):
		Network.__init__(self, self.colour, self.address)
			

	def select(self):
		
		s = self.get_response()
		#print str(self) + ".select gets " + s
		[x,y] = map(int,s.split(" "))
		if x == -1 and y == -1:
			#print str(self) + ".select quits the game"
			with game.lock:
				game.final_state = "network terminated " + self.colour
			game.stop()
		return [x,y]
	def get_move(self):
		s = self.get_response()
		#print str(self) + ".get_move gets " + s
		[x,y] = map(int,s.split(" "))
		if x == -1 and y == -1:
			#print str(self) + ".get_move quits the game"
			with game.lock:
				game.final_state = "network terminated " + self.colour
			game.stop()
		return [x,y]

	def update(self, result):
		
		result = result.split(" ")
		[x,y] = map(int, result[0:2])
		selected = self.board.grid[x][y]
		if selected != None and selected.colour == self.colour and len(result) > 2 and not "->" in result:
			s = self.get_response()
			#print str(self) + ".update - receives " + str(s)
			s = s.split(" ")
			selected.choice = int(s[2])
			for i in range(2):
				selected.types[i] = str(s[3+i])
				if s[3+i] == "unknown":
					selected.types_revealed[i] = False
				else:
					selected.types_revealed[i] = True
			selected.current_type = selected.types[selected.choice]	
		else:
			pass
			#print str(self) + ".update - ignore result " + str(result)			
		

	def quit(self, final_result):
		self.src.close()
	
