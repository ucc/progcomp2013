import socket

class Network():
	def __init__(self, colour, address = None):
		self.socket = socket.socket()

		if colour == "white":
			self.port = 4563
		else:
			self.port = 4564

		self.src = None

		if address == None:
			self.host = 'localhost' #socket.gethostname()
			self.socket.bind((self.host, self.port))
			self.socket.listen(5)	

			self.src, self.address = self.socket.accept()
		else:
			self.host = address
			self.socket.connect(('localhost', self.port))
			self.src = self.socket

	def getline(self):
		s = self.src.recv(1)
		while s[len(s)-1] != '\n':
			s += self.src.recv(1)
		return s
		

		

class NetworkSender(Player,Network):
	def __init__(self, base_player, board, address = None):
		self.base_player = base_player
		Player.__init__(self, base_player.name, base_player.colour)
		Network.__init__(self, base_player.colour, address)

		self.board = board

	def select(self):
		[x,y] = self.base_player.select()
		choice = self.board.grid[x][y]
		s = str(x) + " " + str(y)
		print str(self) + ".select sends " + s
		self.src.send(s + "\n")
		return [x,y]

	def get_move(self):
		[x,y] = self.base_player.get_move()
		s = str(x) + " " + str(y)
		print str(self) + ".get_move sends " + s
		self.src.send(s + "\n")
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
			print str(self) + ".update sends " + s
			self.src.send(s + "\n")
				

	def quit(self, final_result):
		self.base_player.quit(final_result)
		self.src.close()

class NetworkReceiver(Player,Network):
	def __init__(self, colour, board, address=None):
		
		Player.__init__(self, address, colour)

		Network.__init__(self, colour, address)

		self.board = board
			

	def select(self):
		s = self.getline().strip(" \r\n")
		return map(int,s.split(" "))
	def get_move(self):
		s = self.getline().strip(" \r\n")
		print str(self) + ".get_move gets " + s
		return map(int, s.split(" "))

	def update(self, result):
		
		result = result.split(" ")
		[x,y] = map(int, result[0:2])
		selected = self.board.grid[x][y]
		if selected != None and selected.colour == self.colour and len(result) > 2 and not "->" in result:
			s = self.getline().strip(" \r\n")
			print str(self) + ".update - receives " + str(s)
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
			print str(self) + ".update - ignore result " + str(result)			
		

	def quit(self, final_result):
		self.src.close()
	
