import subprocess
import select
import platform

agent_timeout = -1.0 # Timeout in seconds for AI players to make moves
			# WARNING: Won't work for windows based operating systems

if platform.system() == "Windows":
	agent_timeout = -1 # Hence this

# A player who can't play
class Player():
	def __init__(self, name, colour):
		self.name = name
		self.colour = colour

# Player that runs from another process
class AgentPlayer(Player):


	def __init__(self, name, colour):
		Player.__init__(self, name, colour)
		self.p = subprocess.Popen(name, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		
		self.send_message(colour)

	def send_message(self, s):
		if agent_timeout > 0.0:
			ready = select.select([], [self.p.stdin], [], agent_timeout)[1]
		else:
			ready = [self.p.stdin]
		if self.p.stdin in ready:
			#print "Writing to p.stdin"
			try:
				self.p.stdin.write(s + "\n")
			except:
				raise Exception("UNRESPONSIVE")
		else:
			raise Exception("UNRESPONSIVE")

	def get_response(self):
		if agent_timeout > 0.0:
			ready = select.select([self.p.stdout], [], [], agent_timeout)[0]
		else:
			ready = [self.p.stdout]
		if self.p.stdout in ready:
			#print "Reading from p.stdout"
			try:
				return self.p.stdout.readline().strip("\r\n")
			except: # Exception, e:
				raise Exception("UNRESPONSIVE")
		else:
			raise Exception("UNRESPONSIVE")

	def select(self):

		self.send_message("SELECTION?")
		line = self.get_response()
		
		try:
			result = map(int, line.split(" "))
		except:
			raise Exception("GIBBERISH \"" + str(line) + "\"")
		return result

	def update(self, result):
		#print "Update " + str(result) + " called for AgentPlayer"
		self.send_message(result)


	def get_move(self):
		
		self.send_message("MOVE?")
		line = self.get_response()
		
		try:
			result = map(int, line.split(" "))
		except:
			raise Exception("GIBBERISH \"" + str(line) + "\"")
		return result

	def quit(self, final_result):
		try:
			self.send_message("QUIT " + final_result)
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
		if graphics == None:		
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
