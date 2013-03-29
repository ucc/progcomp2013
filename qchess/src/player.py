import subprocess
import select
import platform
import re

agent_timeout = -1.0 # Timeout in seconds for AI players to make moves
			# WARNING: Won't work for windows based operating systems

if platform.system() == "Windows":
	agent_timeout = -1 # Hence this

# A player who can't play
class Player():
	def __init__(self, name, colour):
		self.name = name
		self.colour = colour

	def update(self, result):
		return result

	def reset_board(self, s):
		pass

# Player that runs from another process
class ExternalAgent(Player):


	def __init__(self, name, colour):
		Player.__init__(self, name, colour)
		self.p = subprocess.Popen(name,bufsize=0,stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True,universal_newlines=True)
		
		self.send_message(colour)

	def send_message(self, s):
		if agent_timeout > 0.0:
			ready = select.select([], [self.p.stdin], [], agent_timeout)[1]
		else:
			ready = [self.p.stdin]
		if self.p.stdin in ready:
			#sys.stderr.write("Writing \'" + s + "\' to " + str(self.p) + "\n")
			try:
				self.p.stdin.write(s + "\n")
			except:
				raise Exception("UNRESPONSIVE")
		else:
			raise Exception("TIMEOUT")

	def get_response(self):
		if agent_timeout > 0.0:
			ready = select.select([self.p.stdout], [], [], agent_timeout)[0]
		else:
			ready = [self.p.stdout]
		if self.p.stdout in ready:
			#sys.stderr.write("Reading from " + str(self.p) + " 's stdout...\n")
			try:
				result = self.p.stdout.readline().strip(" \t\r\n")
				#sys.stderr.write("Read \'" + result + "\' from " + str(self.p) + "\n")
				return result
			except: # Exception, e:
				raise Exception("UNRESPONSIVE")
		else:
			raise Exception("TIMEOUT")

	def select(self):

		self.send_message("SELECTION?")
		line = self.get_response()
		
		try:
			m = re.match("\s*(\d+)\s+(\d+)\s*", line)
			result = map(int, [m.group(1), m.group(2)])
		except:
			raise Exception("GIBBERISH \"" + str(line) + "\"")
		return result

	def update(self, result):
		#print "Update " + str(result) + " called for AgentPlayer"
		self.send_message(result)
		return result

	def get_move(self):
		
		self.send_message("MOVE?")
		line = self.get_response()
		
		try:
			m = re.match("\s*(\d+)\s+(\d+)\s*", line)
			result = map(int, [m.group(1), m.group(2)])

		except:
			raise Exception("GIBBERISH \"" + str(line) + "\"")
		return result

	def reset_board(self, s):
		self.send_message("BOARD")
		for line in s.split("\n"):
			self.send_message(line.strip(" \r\n"))
		self.send_message("END BOARD")

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
		return result


# Default internal player (makes random moves)
class InternalAgent(Player):
	def __init__(self, name, colour):
		Player.__init__(self, name, colour)
		self.choice = None

		self.board = Board(style = "agent")



	def update(self, result):
		
		self.board.update(result)
		#self.board.verify()
		return result

	def reset_board(self, s):
		self.board.reset_board(s)

	def quit(self, final_result):
		pass

class AgentRandom(InternalAgent):
	def __init__(self, name, colour):
		InternalAgent.__init__(self, name, colour)

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


# Terrible, terrible hacks

def run_agent(agent):
	#sys.stderr.write(sys.argv[0] + " : Running agent " + str(agent) + "\n")
	while True:
		line = sys.stdin.readline().strip(" \r\n")
		if line == "SELECTION?":
			#sys.stderr.write(sys.argv[0] + " : Make selection\n")
			[x,y] = agent.select() # Gets your agent's selection
			#sys.stderr.write(sys.argv[0] + " : Selection was " + str(agent.choice) + "\n")
			sys.stdout.write(str(x) + " " + str(y) + "\n")				
		elif line == "MOVE?":
			#sys.stderr.write(sys.argv[0] + " : Make move\n")
			[x,y] = agent.get_move() # Gets your agent's move
			sys.stdout.write(str(x) + " " + str(y) + "\n")
		elif line.split(" ")[0] == "QUIT":
			#sys.stderr.write(sys.argv[0] + " : Quitting\n")
			agent.quit(" ".join(line.split(" ")[1:])) # Quits the game
			break
		elif line.split(" ")[0] == "BOARD":
			s = ""
			line = sys.stdin.readline().strip(" \r\n")
			while line != "END BOARD":
				s += line + "\n"
				line = sys.stdin.readline().strip(" \r\n")
			agent.board.reset_board(s)
			
		else:
			agent.update(line) # Updates agent.board
	return 0


# Sort of works?

class ExternalWrapper(ExternalAgent):
	def __init__(self, agent):
		run = "python -u -c \"import sys;import os;from qchess import *;agent = " + agent.__class__.__name__ + "('" + agent.name + "','"+agent.colour+"');sys.stdin.readline();sys.exit(run_agent(agent))\""
		# str(run)
		ExternalAgent.__init__(self, run, agent.colour)

	

