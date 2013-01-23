import subprocess



# A player who can't play
class Player():
	def __init__(self, name, colour):
		self.name = name
		self.colour = colour

# Player that runs from another process
class AgentPlayer(Player):
	def __init__(self, name, colour):
		Player.__init__(self, name, colour)
		self.p = subprocess.Popen(name, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=sys.stderr)
		try:
			self.p.stdin.write(colour + "\n")
		except:
			raise Exception("UNRESPONSIVE")

	def select(self):
		
		#try:
		self.p.stdin.write("SELECTION?\n")
		line = self.p.stdout.readline().strip("\r\n ")
		#except:
		#	raise Exception("UNRESPONSIVE")
		try:
			result = map(int, line.split(" "))
		except:
			raise Exception("GIBBERISH \"" + str(line) + "\"")
		return result

	def update(self, result):
		#print "Update " + str(result) + " called for AgentPlayer"
#		try:
		self.p.stdin.write(result + "\n")
#		except:
#		raise Exception("UNRESPONSIVE")

	def get_move(self):
		
		try:
			self.p.stdin.write("MOVE?\n")
			line = self.p.stdout.readline().strip("\r\n ")
		except:
			raise Exception("UNRESPONSIVE")
		try:
			result = map(int, line.split(" "))
		except:
			raise Exception("GIBBERISH \"" + str(line) + "\"")
		return result

	def quit(self, final_result):
		try:
			self.p.stdin.write("QUIT " + final_result + "\n")
		except:
			self.p.kill()

# So you want to be a player here?
class HumanPlayer(Player):
	def __init__(self, name, colour):
		Player.__init__(self, name, colour)
		
	# Select your preferred account
	def select(self):
		if isinstance(graphics, GraphicsThread):
			# Basically, we let the graphics thread do some shit and then return that information to the game thread
			graphics.cond.acquire()
			# We wait for the graphics thread to select a piece
			while graphics.stopped() == False and graphics.state["select"] == None:
				graphics.cond.wait() # The difference between humans and machines is that humans sleep
			select = graphics.state["select"]
			
			
			graphics.cond.release()
			if graphics.stopped():
				return [-1,-1]
			return [select.x, select.y]
		else:
			# Since I don't display the board in this case, I'm not sure why I filled it in...
			while True:
				sys.stdout.write("SELECTION?\n")
				try:
					p = map(int, sys.stdin.readline().strip("\r\n ").split(" "))
				except:
					sys.stderr.write("ILLEGAL GIBBERISH\n")
					continue
	# It's your move captain
	def get_move(self):
		if isinstance(graphics, GraphicsThread):
			graphics.cond.acquire()
			while graphics.stopped() == False and graphics.state["dest"] == None:
				graphics.cond.wait()
			graphics.cond.release()
			
			return graphics.state["dest"]
		else:

			while True:
				sys.stdout.write("MOVE?\n")
				try:
					p = map(int, sys.stdin.readline().strip("\r\n ").split(" "))
				except:
					sys.stderr.write("ILLEGAL GIBBERISH\n")
					continue

	# Are you sure you want to quit?
	def quit(self, final_result):
		sys.stdout.write("QUIT " + final_result + "\n")

	# Completely useless function
	def update(self, result):
		if isinstance(graphics, GraphicsThread):
			pass
		else:
			sys.stdout.write(result + "\n")	


# Player that makes random moves
class AgentRandom(Player):
	def __init__(self, name, colour):
		Player.__init__(self, name, colour)
		self.choice = None

		self.board = Board(style = "agent")

	def select(self):
		while True:
			self.choice = self.board.pieces[self.colour][random.randint(0, len(self.board.pieces[self.colour])-1)]
			all_moves = []
			# Check that the piece has some possibility to move
			tmp = self.choice.current_type
			if tmp == "unknown": # For unknown pieces, try both types
				for t in self.choice.types:
					if t == "unknown":
						continue
					self.choice.current_type = t
					all_moves += self.board.possible_moves(self.choice)
			else:
				all_moves = self.board.possible_moves(self.choice)
			self.choice.current_type = tmp
			if len(all_moves) > 0:
				break
		return [self.choice.x, self.choice.y]

	def get_move(self):
		moves = self.board.possible_moves(self.choice)
		move = moves[random.randint(0, len(moves)-1)]
		return move

	def update(self, result):
		#sys.stderr.write(sys.argv[0] + " : Update board for AgentRandom\n")
		self.board.update(result)
		self.board.verify()

	def quit(self, final_result):
		pass
