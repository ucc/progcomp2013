#!/usr/bin/python -u
import random

# I know using non-abreviated strings is inefficient, but this is python, who cares?
# Oh, yeah, this stores the number of pieces of each type in a normal chess game
piece_types = {"pawn" : 8, "bishop" : 2, "knight" : 2, "rook" : 2, "queen" : 1, "king" : 1, "unknown" : 0}

# Class to represent a quantum chess piece
class Piece():
	def __init__(self, colour, x, y, types):
		self.colour = colour # Colour (string) either "white" or "black"
		self.x = x # x coordinate (0 - 8), none of this fancy 'a', 'b' shit here
		self.y = y # y coordinate (0 - 8)
		self.types = types # List of possible types the piece can be (should just be two)
		self.current_type = "unknown" # Current type
		self.choice = -1 # Index of the current type in self.types (-1 = unknown type)
		self.types_revealed = [True, False] # Whether the types are known (by default the first type is always known at game start)
		

		# 
		self.last_state = None
		self.move_pattern = None

		

	def init_from_copy(self, c):
		self.colour = c.colour
		self.x = c.x
		self.y = c.y
		self.types = c.types[:]
		self.current_type = c.current_type
		self.choice = c.choice
		self.types_revealed = c.types_revealed[:]

		self.last_state = None
		self.move_pattern = None

	

	# Make a string for the piece (used for debug)
	def __str__(self):
		return str(self.colour) + " " + str(self.current_type) + " " + str(self.types) + " at " + str(self.x) + ","+str(self.y)  

	# Draw the piece in a pygame surface
	def draw(self, window, grid_sz = [80,80], style="quantum"):

		# First draw the image corresponding to self.current_type
		img = images[self.colour][self.current_type]
		rect = img.get_rect()
		if style == "classical":
			offset = [-rect.width/2, -rect.height/2]
		else:
			offset = [-rect.width/2,-3*rect.height/4] 
		window.blit(img, (self.x * grid_sz[0] + grid_sz[0]/2 + offset[0], self.y * grid_sz[1] + grid_sz[1]/2 + offset[1]))
		
		
		if style == "classical":
			return

		# Draw the two possible types underneath the current_type image
		for i in range(len(self.types)):
			if always_reveal_states == True or self.types_revealed[i] == True:
				img = small_images[self.colour][self.types[i]]
			else:
				img = small_images[self.colour]["unknown"] # If the type hasn't been revealed, show a placeholder

			
			rect = img.get_rect()
			offset = [-rect.width/2,-rect.height/2] 
			
			if i == 0:
				target = (self.x * grid_sz[0] + grid_sz[0]/5 + offset[0], self.y * grid_sz[1] + 3*grid_sz[1]/4 + offset[1])				
			else:
				target = (self.x * grid_sz[0] + 4*grid_sz[0]/5 + offset[0], self.y * grid_sz[1] + 3*grid_sz[1]/4 + offset[1])				
				
			window.blit(img, target) # Blit shit
	
	# Collapses the wave function!		
	def select(self):
		if self.current_type == "unknown":
			self.choice = random.randint(0,1)
			self.current_type = self.types[self.choice]
			self.types_revealed[self.choice] = True
		return self.choice

	# Uncollapses (?) the wave function!
	def deselect(self):
		#print "Deselect called"
		if (self.x + self.y) % 2 != 0:
			if (self.types[0] != self.types[1]) or (self.types_revealed[0] == False or self.types_revealed[1] == False):
				self.current_type = "unknown"
				self.choice = -1
			else:
				self.choice = 0 # Both the two types are the same

	# The sad moment when you realise that you do not understand anything about a subject you studied for 4 years...
# --- piece.py --- #
[w,h] = [8,8] # Width and height of board(s)

always_reveal_states = False

# Class to represent a quantum chess board
class Board():
	# Initialise; if master=True then the secondary piece types are assigned
	#	Otherwise, they are left as unknown
	#	So you can use this class in Agent programs, and fill in the types as they are revealed
	def __init__(self, style="agent"):
		self.style = style
		self.pieces = {"white" : [], "black" : []}
		self.grid = [[None] * w for _ in range(h)] # 2D List (you can get arrays in python, somehow, but they scare me)
		self.unrevealed_types = {"white" : piece_types.copy(), "black" : piece_types.copy()}
		self.king = {"white" : None, "black" : None} # We need to keep track of the king, because he is important
		for c in ["black", "white"]:
			del self.unrevealed_types[c]["unknown"]

		if style == "empty":
			return

		# Add all the pieces with known primary types
		for i in range(0, 2):
			
			s = ["black", "white"][i]
			c = self.pieces[s]
			y = [0, h-1][i]

			c.append(Piece(s, 0, y, ["rook"]))
			c.append(Piece(s, 1, y, ["knight"]))
			c.append(Piece(s, 2, y, ["bishop"]))
			k = Piece(s, 3, y, ["king", "king"]) # There can only be one ruler!
			k.types_revealed[1] = True
			k.current_type = "king"
			self.king[s] = k
			c.append(k)
			c.append(Piece(s, 4, y, ["queen"])) # Apparently he may have multiple wives though.
			c.append(Piece(s, 5, y, ["bishop"]))
			c.append(Piece(s, 6, y, ["knight"]))
			c.append(Piece(s, 7, y, ["rook"]))
			
			if y == 0: 
				y += 1 
			else: 
				y -= 1
			
			# Lots of pawn
			for x in range(0, w):
				c.append(Piece(s, x, y, ["pawn"]))

			types_left = {}
			types_left.update(piece_types)
			del types_left["king"] # We don't want one of these randomly appearing (although it might make things interesting...)
			del types_left["unknown"] # We certainly don't want these!
			for piece in c:
				# Add to grid
				self.grid[piece.x][piece.y] = piece 

				if len(piece.types) > 1:
					continue				
				if style == "agent": # Assign placeholder "unknown" secondary type
					piece.types.append("unknown")
					continue

				elif style == "quantum":
					# The master allocates the secondary types
					choice = types_left.keys()[random.randint(0, len(types_left.keys())-1)]
					types_left[choice] -= 1
					if types_left[choice] <= 0:
						del types_left[choice]
					piece.types.append(choice)
				elif style == "classical":
					piece.types.append(piece.types[0])
					piece.current_type = piece.types[0]
					piece.types_revealed[1] = True
					piece.choice = 0

	def clone(self):
		newboard = Board(master = False)
		newpieces = newboard.pieces["white"] + newboard.pieces["black"]
		mypieces = self.pieces["white"] + self.pieces["black"]

		for i in range(len(mypieces)):
			newpieces[i].init_from_copy(mypieces[i])
			

	def display_grid(self, window = None, grid_sz = [80,80]):
		if window == None:
			return # I was considering implementing a text only display, then I thought "Fuck that"

		# The indentation is getting seriously out of hand...
		for x in range(0, w):
			for y in range(0, h):
				if (x + y) % 2 == 0:
					c = pygame.Color(200,200,200)
				else:
					c = pygame.Color(64,64,64)
				pygame.draw.rect(window, c, (x*grid_sz[0], y*grid_sz[1], (x+1)*grid_sz[0], (y+1)*grid_sz[1]))

	def display_pieces(self, window = None, grid_sz = [80,80]):
		if window == None:
			return
		for p in self.pieces["white"] + self.pieces["black"]:
			p.draw(window, grid_sz, self.style)

	# Draw the board in a pygame window
	def display(self, window = None):
		self.display_grid(window)
		self.display_pieces(window)
		

		

	def verify(self):
		for x in range(w):
			for y in range(h):
				if self.grid[x][y] == None:
					continue
				if (self.grid[x][y].x != x or self.grid[x][y].y != y):
					raise Exception(sys.argv[0] + ": MISMATCH " + str(self.grid[x][y]) + " should be at " + str(x) + "," + str(y))

	# Select a piece on the board (colour is the colour of whoever is doing the selecting)
	def select(self, x,y, colour=None):
		if not self.on_board(x, y): # Get on board everyone!
			raise Exception("BOUNDS")

		piece = self.grid[x][y]
		if piece == None:
			raise Exception("EMPTY")

		if colour != None and piece.colour != colour:
			raise Exception("COLOUR " + str(piece.colour) + " not " + str(colour))

		# I'm not quite sure why I made this return a string, but screw logical design
		return str(x) + " " + str(y) + " " + str(piece.select()) + " " + str(piece.current_type)


	# Update the board when a piece has been selected
	# "type" is apparently reserved, so I'll use "state"
	def update_select(self, x, y, type_index, state):
		piece = self.grid[x][y]
		if piece.types[type_index] == "unknown":
			if not state in self.unrevealed_types[piece.colour].keys():
				raise Exception("SANITY: Too many " + piece.colour + " " + state + "s")
			self.unrevealed_types[piece.colour][state] -= 1
			if self.unrevealed_types[piece.colour][state] <= 0:
				del self.unrevealed_types[piece.colour][state]

		piece.types[type_index] = state
		piece.types_revealed[type_index] = True
		piece.current_type = state

		if len(self.possible_moves(piece)) <= 0:
			piece.deselect() # Piece can't move; deselect it
		
	# Update the board when a piece has been moved
	def update_move(self, x, y, x2, y2):
		piece = self.grid[x][y]
		self.grid[x][y] = None
		taken = self.grid[x2][y2]
		if taken != None:
			if taken.current_type == "king":
				self.king[taken.colour] = None
			self.pieces[taken.colour].remove(taken)
		self.grid[x2][y2] = piece
		piece.x = x2
		piece.y = y2

		# If the piece is a pawn, and it reaches the final row, it becomes a queen
		# I know you are supposed to get a choice
		# But that would be effort
		if piece.current_type == "pawn" and ((piece.colour == "white" and piece.y == 0) or (piece.colour == "black" and piece.y == h-1)):
			if self.style == "classical":
				piece.types[0] = "queen"
				piece.types[1] = "queen"
			else:
				piece.types[piece.choice] = "queen"
			piece.current_type = "queen"

		piece.deselect() # Uncollapse (?) the wavefunction!
		self.verify()	

	# Update the board from a string
	# Guesses what to do based on the format of the string
	def update(self, result):
		#print "Update called with \"" + str(result) + "\""
		# String always starts with 'x y'
		try:
			s = result.split(" ")
			[x,y] = map(int, s[0:2])	
		except:
			raise Exception("GIBBERISH \""+ str(result) + "\"") # Raise expectations

		piece = self.grid[x][y]
		if piece == None:
			raise Exception("EMPTY")

		# If a piece is being moved, the third token is '->'
		# We could get away with just using four integers, but that wouldn't look as cool
		if "->" in s:
			# Last two tokens are the destination
			try:
				[x2,y2] = map(int, s[3:])
			except:
				raise Exception("GIBBERISH \"" + str(result) + "\"") # Raise the alarm

			# Move the piece (take opponent if possible)
			self.update_move(x, y, x2, y2)
			
		else:
			# Otherwise we will just assume a piece has been selected
			try:
				type_index = int(s[2]) # We need to know which of the two types the piece is in; that's the third token
				state = s[3] # The last token is a string identifying the type
			except:
				raise Exception("GIBBERISH \"" + result + "\"") # Throw a hissy fit

			# Select the piece
			self.update_select(x, y, type_index, state)

		return result

	# Gets each piece that could reach the given square and the probability that it could reach that square	
	# Will include allied pieces that defend the attacker
	def coverage(self, x, y, colour = None, reject_allied = True):
		result = {}
		
		if colour == None:
			pieces = self.pieces["white"] + self.pieces["black"]
		else:
			pieces = self.pieces[colour]

		for p in pieces:
			prob = self.probability_grid(p, reject_allied)[x][y]
			if prob > 0:
				result.update({p : prob})
		
		self.verify()
		return result


		


	# Associates each square with a probability that the piece could move into it
	# Look, I'm doing all the hard work for you here...
	def probability_grid(self, p, reject_allied = True):
		
		result = [[0.0] * w for _ in range(h)]
		if not isinstance(p, Piece):
			return result

		if p.current_type != "unknown":
			#sys.stderr.write(sys.argv[0] + ": " + str(p) + " moves " + str(self.possible_moves(p, reject_allied)) + "\n")
			for point in self.possible_moves(p, reject_allied):
				result[point[0]][point[1]] = 1.0
			return result
		
		
		for i in range(len(p.types)):
			t = p.types[i]
			prob = 0.5
			if t == "unknown" or p.types_revealed[i] == False:
				total_types = 0
				for t2 in self.unrevealed_types[p.colour].keys():
					total_types += self.unrevealed_types[p.colour][t2]
				
				for t2 in self.unrevealed_types[p.colour].keys():
					prob2 = float(self.unrevealed_types[p.colour][t2]) / float(total_types)
					p.current_type = t2
					for point in self.possible_moves(p, reject_allied):
						result[point[0]][point[1]] += prob2 * prob
				
			else:
				p.current_type = t
				for point in self.possible_moves(p, reject_allied):
					result[point[0]][point[1]] += prob
		
		self.verify()
		p.current_type = "unknown"
		return result

	def prob_is_type(self, p, state):
		prob = 0.5
		result = 0
		for i in range(len(p.types)):
			t = p.types[i]
			if t == state:
				result += prob
				continue	
			if t == "unknown" or p.types_revealed[i] == False:
				total_prob = 0
				for t2 in self.unrevealed_types[p.colour].keys():
					total_prob += self.unrevealed_types[p.colour][t2]
				for t2 in self.unrevealed_types[p.colour].keys():
					if t2 == state:
						result += prob * float(self.unrevealed_types[p.colour][t2]) / float(total_prob)
				


	# Get all squares that the piece could move into
	# This is probably inefficient, but I looked at some sample chess games and they seem to actually do things this way
	# reject_allied indicates whether squares occupied by allied pieces will be removed
	# (set to false to check for defense)
	def possible_moves(self, p, reject_allied = True):
		result = []
		if p == None:
			return result

		
		if p.current_type == "unknown":
			raise Exception("SANITY: Piece state unknown")
			# The below commented out code causes things to break badly
			#for t in p.types:
			#	if t == "unknown":
			#		continue
			#	p.current_type = t
			#	result += self.possible_moves(p)						
			#p.current_type = "unknown"
			#return result

		if p.current_type == "king":
			result = [[p.x-1,p.y],[p.x+1,p.y],[p.x,p.y-1],[p.x,p.y+1], [p.x-1,p.y-1],[p.x-1,p.y+1],[p.x+1,p.y-1],[p.x+1,p.y+1]]
		elif p.current_type == "queen":
			for d in [[-1,0],[1,0],[0,-1],[0,1],[-1,-1],[-1,1],[1,-1],[1,1]]:
				result += self.scan(p.x, p.y, d[0], d[1])
		elif p.current_type == "bishop":
			for d in [[-1,-1],[-1,1],[1,-1],[1,1]]: # There's a reason why bishops move diagonally
				result += self.scan(p.x, p.y, d[0], d[1])
		elif p.current_type == "rook":
			for d in [[-1,0],[1,0],[0,-1],[0,1]]:
				result += self.scan(p.x, p.y, d[0], d[1])
		elif p.current_type == "knight":
			# I would use two lines, but I'm not sure how python likes that
			result = [[p.x-2, p.y-1], [p.x-2, p.y+1], [p.x+2, p.y-1], [p.x+2,p.y+1], [p.x-1,p.y-2], [p.x-1, p.y+2],[p.x+1,p.y-2],[p.x+1,p.y+2]]
		elif p.current_type == "pawn":
			if p.colour == "white":
				
				# Pawn can't move forward into occupied square
				if self.on_board(p.x, p.y-1) and self.grid[p.x][p.y-1] == None:
					result = [[p.x,p.y-1]]
				for f in [[p.x-1,p.y-1],[p.x+1,p.y-1]]:
					if not self.on_board(f[0], f[1]):
						continue
					if self.grid[f[0]][f[1]] != None:  # Pawn can take diagonally
						result.append(f)
				if p.y == h-2:
					# Slightly embarrassing if the pawn jumps over someone on its first move...
					if self.grid[p.x][p.y-1] == None and self.grid[p.x][p.y-2] == None:
						result.append([p.x, p.y-2])
			else:
				# Vice versa for the black pawn
				if self.on_board(p.x, p.y+1) and self.grid[p.x][p.y+1] == None:
					result = [[p.x,p.y+1]]

				for f in [[p.x-1,p.y+1],[p.x+1,p.y+1]]:
					if not self.on_board(f[0], f[1]):
						continue
					if self.grid[f[0]][f[1]] != None:
						#sys.stderr.write(sys.argv[0] + " : "+str(p) + " can take " + str(self.grid[f[0]][f[1]]) + "\n")
						result.append(f)
				if p.y == 1:
					if self.grid[p.x][p.y+1] == None and self.grid[p.x][p.y+2] == None:
						result.append([p.x, p.y+2])

			#sys.stderr.write(sys.argv[0] + " : possible_moves for " + str(p) + " " + str(result) + "\n")

		# Remove illegal moves
		# Note: The result[:] creates a copy of result, so that the result.remove calls don't fuck things up
		for point in result[:]: 

			if (point[0] < 0 or point[0] >= w) or (point[1] < 0 or point[1] >= h):
				result.remove(point) # Remove locations outside the board
				continue
			g = self.grid[point[0]][point[1]]
			
			if g != None and (g.colour == p.colour and reject_allied == True):
				result.remove(point) # Remove allied pieces
		
		self.verify()
		return result


	# Scans in a direction until it hits a piece, returns all squares in the line
	# (includes the final square (which contains a piece), but not the original square)
	def scan(self, x, y, vx, vy):
		p = []
			
		xx = x
		yy = y
		while True:
			xx += vx
			yy += vy
			if not self.on_board(xx, yy):
				break
			if not [xx,yy] in p:
				p.append([xx, yy])
			g = self.grid[xx][yy]
			if g != None:
				return p	
					
		return p



	# I typed the full statement about 30 times before writing this function...
	def on_board(self, x, y):
		return (x >= 0 and x < w) and (y >= 0 and y < h)
# --- board.py --- #
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

	def update(self, result):
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
				result = self.p.stdout.readline().strip("\r\n")
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


# Default internal player (makes random moves)
class InternalAgent(Player):
	def __init__(self, name, colour):
		Player.__init__(self, name, colour)
		self.choice = None

		self.board = Board(style = "agent")



	def update(self, result):
		
		self.board.update(result)
		self.board.verify()

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
		else:
			agent.update(line) # Updates agent.board
	return 0


# Sort of works?

class ExternalWrapper(ExternalAgent):
	def __init__(self, agent):
		run = "python -u -c \"import sys;import os;from qchess import *;agent = " + agent.__class__.__name__ + "('" + agent.name + "','"+agent.colour+"');sys.stdin.readline();sys.exit(run_agent(agent))\""
		# str(run)
		ExternalAgent.__init__(self, run, agent.colour)

	

# --- player.py --- #
# A sample agent


class AgentBishop(InternalAgent): # Inherits from InternalAgent (in qchess)
	def __init__(self, name, colour):
		InternalAgent.__init__(self, name, colour)
		self.value = {"pawn" : 1, "bishop" : 3, "knight" : 3, "rook" : 5, "queen" : 9, "king" : 100, "unknown" : 4}

		self.aggression = 2.0 # Multiplier for scoring due to aggressive actions
		self.defence = 1.0 # Multiplier for scoring due to defensive actions
		
		self.depth = 0 # Current depth
		self.max_depth = 2 # Recurse this many times (for some reason, makes more mistakes when this is increased???)
		self.recurse_for = -1 # Recurse for the best few moves each times (less than 0 = all moves)

		for p in self.board.pieces["white"] + self.board.pieces["black"]:
			p.last_moves = None
			p.selected_moves = None

		

	def get_value(self, piece):
		if piece == None:
			return 0.0
		return float(self.value[piece.types[0]] + self.value[piece.types[1]]) / 2.0
		
	# Score possible moves for the piece
	
	def prioritise_moves(self, piece):

		#sys.stderr.write(sys.argv[0] + " : " + str(self) + " prioritise called for " + str(piece) + "\n")

		
		
		grid = self.board.probability_grid(piece)
		#sys.stderr.write("\t Probability grid " + str(grid) + "\n")
		moves = []
		for x in range(w):
			for y in range(h):
				if grid[x][y] < 0.3: # Throw out moves with < 30% probability
					#sys.stderr.write("\tReject " + str(x) + "," + str(y) + " (" + str(grid[x][y]) + ")\n")
					continue

				target = self.board.grid[x][y]
			
				
				
				
				# Get total probability that the move is protected
				[xx,yy] = [piece.x, piece.y]
				[piece.x, piece.y] = [x, y]
				self.board.grid[x][y] = piece
				self.board.grid[xx][yy] = None
				
				defenders = self.board.coverage(x, y, piece.colour, reject_allied = False)
				d_prob = 0.0
				for d in defenders.keys():
					d_prob += defenders[d]
				if len(defenders.keys()) > 0:
					d_prob /= float(len(defenders.keys()))

				if (d_prob > 1.0):
					d_prob = 1.0

				# Get total probability that the move is threatened
				attackers = self.board.coverage(x, y, opponent(piece.colour), reject_allied = False)
				a_prob = 0.0
				for a in attackers.keys():
					a_prob += attackers[a]
				if len(attackers.keys()) > 0:
					a_prob /= float(len(attackers.keys()))

				if (a_prob > 1.0):
					a_prob = 1.0

				self.board.grid[x][y] = target
				self.board.grid[xx][yy] = piece
				[piece.x, piece.y] = [xx, yy]

				
				# Score of the move
				value = self.aggression * (1.0 + d_prob) * self.get_value(target) - self.defence * (1.0 - d_prob) * a_prob * self.get_value(piece)

				# Adjust score based on movement of piece out of danger
				attackers = self.board.coverage(piece.x, piece.y, opponent(piece.colour))
				s_prob = 0.0
				for a in attackers.keys():
					s_prob += attackers[a]
				if len(attackers.keys()) > 0:
					s_prob /= float(len(attackers.keys()))

				if (s_prob > 1.0):
					s_prob = 1.0
				value += self.defence * s_prob * self.get_value(piece)
				
				# Adjust score based on probability that the move is actually possible
				moves.append([[x, y], grid[x][y] * value])

		moves.sort(key = lambda e : e[1], reverse = True)
		#sys.stderr.write(sys.argv[0] + ": Moves for " + str(piece) + " are " + str(moves) + "\n")

		piece.last_moves = moves
		piece.selected_moves = None

		

		
		return moves

	def select_best(self, colour):

		self.depth += 1
		all_moves = {}
		for p in self.board.pieces[colour]:
			self.choice = p # Temporarily pick that piece
			m = self.prioritise_moves(p)
			if len(m) > 0:
				all_moves.update({p : m[0]})

		if len(all_moves.items()) <= 0:
			return None
		
		
		opts = all_moves.items()
		opts.sort(key = lambda e : e[1][1], reverse = True)

		if self.depth >= self.max_depth:
			self.depth -= 1
			return list(opts[0])

		if self.recurse_for >= 0:
			opts = opts[0:self.recurse_for]
		#sys.stderr.write(sys.argv[0] + " : Before recurse, options are " + str(opts) + "\n")

		# Take the best few moves, and recurse
		for choice in opts[0:self.recurse_for]:
			[xx,yy] = [choice[0].x, choice[0].y] # Remember position
			[nx,ny] = choice[1][0] # Target
			[choice[0].x, choice[0].y] = [nx, ny] # Set position
			target = self.board.grid[nx][ny] # Remember piece in spot
			self.board.grid[xx][yy] = None # Remove piece
			self.board.grid[nx][ny] = choice[0] # Replace with moving piece
			
			# Recurse
			best_enemy_move = self.select_best(opponent(choice[0].colour))
			choice[1][1] -= best_enemy_move[1][1] / float(self.depth + 1.0)
			
			[choice[0].x, choice[0].y] = [xx, yy] # Restore position
			self.board.grid[nx][ny] = target # Restore taken piece
			self.board.grid[xx][yy] = choice[0] # Restore moved piece
			
		

		opts.sort(key = lambda e : e[1][1], reverse = True)
		#sys.stderr.write(sys.argv[0] + " : After recurse, options are " + str(opts) + "\n")

		self.depth -= 1
		return list(opts[0])

		

	# Returns [x,y] of selected piece
	def select(self):
		#sys.stderr.write("Getting choice...")
		self.choice = self.select_best(self.colour)[0]
		#sys.stderr.write(" Done " + str(self.choice)+"\n")
		return [self.choice.x, self.choice.y]
	
	# Returns [x,y] of square to move selected piece into
	def get_move(self):
		#sys.stderr.write("Choice is " + str(self.choice) + "\n")
		self.choice.selected_moves = self.choice.last_moves
		moves = self.prioritise_moves(self.choice)
		if len(moves) > 0:
			return moves[0][0]
		else:
			return InternalAgent.get_move(self)

# --- agent_bishop.py --- #
import multiprocessing

# Hacky alternative to using select for timing out players

# WARNING: Do not wrap around HumanPlayer or things breakify
# WARNING: Do not use in general or things breakify

class Sleeper(multiprocessing.Process):
	def __init__(self, timeout):
		multiprocessing.Process.__init__(self)
		self.timeout = timeout

	def run(self):
		time.sleep(self.timeout)


class Worker(multiprocessing.Process):
	def __init__(self, function, args, q):
		multiprocessing.Process.__init__(self)
		self.function = function
		self.args = args
		self.q = q

	def run(self):
		#print str(self) + " runs " + str(self.function) + " with args " + str(self.args) 
		self.q.put(self.function(*self.args))
		
		

def TimeoutFunction(function, args, timeout):
	q = multiprocessing.Queue()
	w = Worker(function, args, q)
	s = Sleeper(timeout)
	w.start()
	s.start()
	while True: # Busy loop of crappyness
		if not w.is_alive():
			s.terminate()
			result = q.get()
			w.join()
			#print "TimeoutFunction gets " + str(result)
			return result
		elif not s.is_alive():
			w.terminate()
			s.join()
			raise Exception("TIMEOUT")

	
		

# A player that wraps another player and times out its moves
# Uses threads
# A (crappy) alternative to the use of select()
class TimeoutPlayer(Player):
	def __init__(self, base_player, timeout):
		Player.__init__(self, base_player.name, base_player.colour)
		self.base_player = base_player
		self.timeout = timeout
		
	def select(self):
		return TimeoutFunction(self.base_player.select, [], self.timeout)
		
	
	def get_move(self):
		return TimeoutFunction(self.base_player.get_move, [], self.timeout)

	def update(self, result):
		return TimeoutFunction(self.base_player.update, [result], self.timeout)

	def quit(self, final_result):
		return TimeoutFunction(self.base_player.quit, [final_result], self.timeout)
# --- timeout_player.py --- #
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
	
# --- network.py --- #
import threading

# A thread that can be stopped!
# Except it can only be stopped if it checks self.stopped() periodically
# So it can sort of be stopped
class StoppableThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self._stop = threading.Event()

	def stop(self):
		self._stop.set()

	def stopped(self):
		return self._stop.isSet()
# --- thread_util.py --- #
log_file = None
import datetime
import urllib2

class LogFile():
	def __init__(self, log):	
		
		self.log = log
		self.logged = []

	def write(self, s):
		now = datetime.datetime.now()
		self.log.write(str(now) + " : " + s + "\n")
		self.logged.append((now, s))

	def setup(self, board, players):
		self.log.write("# Log starts " + str(datetime.datetime.now()) + "\n")
		for p in players:
			self.log.write("# " + p.colour + " : " + p.name + "\n")
		
		self.log.write("# Initial board\n")
		for x in range(0, w):
			for y in range(0, h):
				if board.grid[x][y] != None:
					self.log.write(str(board.grid[x][y]) + "\n")

		self.log.write("# Start game\n")

	def close(self):
		self.log.write("# EOF\n")
		self.log.close()

class HttpLog(LogFile):
	def __init__(self, file_name):
		LogFile.__init__(self, open(file_name, "w", 0))
		self.file_name = file_name
		self.phase = 0

	def write(self, s):
		now = datetime.datetime.now()
		self.logged.append((now, s))
		
		if self.phase == 0:
			self.log.close()
			self.log = open(self.file_name, "w", 0)
			LogFile.setup(self, game.board, game.players)

		elif self.phase == 1:
			for message in self.logged[len(self.logged)-2:]:
				self.log.write(str(message[0]) + " : " + message[1] + "\n")

		self.phase = (self.phase + 1) % 2		
		
	def close(self):
		self.log.write("# EOF\n")
		self.log.close()
		

class HeadRequest(urllib2.Request):
	def get_method(self):
		return "HEAD"
		
class HttpReplay():
	def __init__(self, address):
		self.read_setup = False
		self.log = urllib2.urlopen(address)
		self.address = address

	def readline(self):
		
		line = self.log.readline()
		sys.stderr.write(sys.argv[0] + " : " + str(self.__class__.__name__) + " read \""+str(line.strip("\r\n")) + "\" from address " + str(self.address) + "\n")
		if line == "":
			sys.stderr.write(sys.argv[0] + " : " + str(self.__class__.__name__) + " retrieving from address " + str(self.address) + "\n")
			date_mod = datetime.datetime.strptime(self.log.headers['last-modified'], "%a, %d %b %Y %H:%M:%S GMT")
			self.log.close()

			next_log = urllib2.urlopen(HeadRequest(self.address))
			date_new = datetime.datetime.strptime(next_log.headers['last-modified'], "%a, %d %b %Y %H:%M:%S GMT")
			while date_new <= date_mod:
				next_log = urllib2.urlopen(HeadRequest(self.address))
				date_new = datetime.datetime.strptime(next_log.headers['last-modified'], "%a, %d %b %Y %H:%M:%S GMT")

			self.log = urllib2.urlopen(self.address)
			game.setup()
			line = self.log.readline()


		return line
			
	def close(self):
		self.log.close()
						
def log(s):
	if log_file != None:
		log_file.write(s)
		

def log_init(board, players):
	if log_file != None:
		log_file.setup(board, players)

# --- log.py --- #



	

# A thread that runs the game
class GameThread(StoppableThread):
	def __init__(self, board, players):
		StoppableThread.__init__(self)
		self.board = board
		self.players = players
		self.state = {"turn" : None} # The game state
		self.error = 0 # Whether the thread exits with an error
		self.lock = threading.RLock() #lock for access of self.state
		self.cond = threading.Condition() # conditional for some reason, I forgot
		self.final_result = ""
		
		

	# Run the game (run in new thread with start(), run in current thread with run())
	def run(self):
		result = ""
		while not self.stopped():
			
			for p in self.players:
				with self.lock:
					if isinstance(p, NetworkSender):
						self.state["turn"] = p.base_player # "turn" contains the player who's turn it is
					else:
						self.state["turn"] = p
				#try:
				if True:
					[x,y] = p.select() # Player selects a square
					if self.stopped():
						break

					
						

					result = self.board.select(x, y, colour = p.colour)				
					for p2 in self.players:
						p2.update(result) # Inform players of what happened


					log(result)

					target = self.board.grid[x][y]
					if isinstance(graphics, GraphicsThread):
						with graphics.lock:
							graphics.state["moves"] = self.board.possible_moves(target)
							graphics.state["select"] = target

					time.sleep(turn_delay)


					if len(self.board.possible_moves(target)) == 0:
						#print "Piece cannot move"
						target.deselect()
						if isinstance(graphics, GraphicsThread):
							with graphics.lock:
								graphics.state["moves"] = None
								graphics.state["select"] = None
								graphics.state["dest"] = None
						continue

					try:
						[x2,y2] = p.get_move() # Player selects a destination
					except:
						self.stop()

					if self.stopped():
						break

					result = str(x) + " " + str(y) + " -> " + str(x2) + " " + str(y2)
					log(result)

					self.board.update_move(x, y, x2, y2)
					
					for p2 in self.players:
						p2.update(result) # Inform players of what happened

										

					if isinstance(graphics, GraphicsThread):
						with graphics.lock:
							graphics.state["moves"] = [[x2,y2]]

					time.sleep(turn_delay)

					if isinstance(graphics, GraphicsThread):
						with graphics.lock:
							graphics.state["select"] = None
							graphics.state["dest"] = None
							graphics.state["moves"] = None

			# Commented out exception stuff for now, because it makes it impossible to tell if I made an IndentationError somewhere
			#	except Exception,e:
			#		result = e.message
			#		#sys.stderr.write(result + "\n")
			#		
			#		self.stop()
			#		with self.lock:
			#			self.final_result = self.state["turn"].colour + " " + e.message

				if self.board.king["black"] == None:
					if self.board.king["white"] == None:
						with self.lock:
							self.final_result = self.state["turn"].colour + " DRAW"
					else:
						with self.lock:
							self.final_result = "white"
					self.stop()
				elif self.board.king["white"] == None:
					with self.lock:
						self.final_result = "black"
					self.stop()
						

				if self.stopped():
					break


		for p2 in self.players:
			p2.quit(self.final_result)

		log(self.final_result)

		if isinstance(graphics, GraphicsThread):
			graphics.stop()

	
# A thread that replays a log file
class ReplayThread(GameThread):
	def __init__(self, players, src, end=False,max_lines=None):
		self.board = Board(style="empty")
		GameThread.__init__(self, self.board, players)
		self.src = src
		self.max_lines = max_lines
		self.line_number = 0
		self.end = end

		self.reset_board(self.src.readline())

	def reset_board(self, line):
		pieces = {"white" : [], "black" : []}
		king = {"white" : None, "black" : None}
		for x in range(w):
			for y in range(h):
				self.board.grid[x][y] = None
		while line != "# Start game":
			tokens = line.split(" ")
			[x, y] = map(int, tokens[len(tokens)-1].split(","))
			current_type = tokens[1]
			types = map(lambda e : e.strip("'[], "), tokens[2].split(","))

			target = Piece(tokens[0], x, y, current_type)
			try:
				target.choice = types.index(current_type)
			except:
				target.choice = -1

			pieces[token[0]].append(target)
			if target.current_type == "king":
				king[token[0]] = target
		
			line = self.src.readline().strip(" \r\n")

		self.board.pieces = pieces
		self.board.king = king
	
	def run(self):
		move_count = 0
		line = self.src.readline().strip(" \r\n")
		while line != "# EOF":
			if self.stopped():
				break

					

			if line[0] == '#':
				line = self.src.readline().strip(" \r\n")
				continue

			tokens = line.split(" ")
			if tokens[0] == "white" or tokens[0] == "black":
				self.reset_board(line)
				line = self.src.readline().strip(" \r\n")
				continue

			move = line.split(":")[1]
			tokens = move.split(" ")
			try:
				[x,y] = map(int, tokens[0:2])
			except:
				self.stop()
				break

			target = self.board.grid[x][y]
			
			move_piece = (tokens[2] == "->")

			if move_piece:
				[x2,y2] = map(int, tokens[len(tokens)-2:])

			log(move)
			self.board.update(move)
			for p in self.players:
				p.update(move)
			
			if isinstance(graphics, GraphicsThread):
				with self.lock:
					if target.colour == "white":
						self.state["turn"] = self.players[0]
					else:
						self.state["turn"] = self.players[1]

				with graphics.lock:
					graphics.state["select"] = target
					if move_piece:
						graphics.state["moves"] = [[x2, y2]]
					elif target.current_type != "unknown":
						graphics.state["moves"] = self.board.possible_moves(target)
					


			

				
			

		if self.max_lines != None and self.max_lines > count:
			sys.stderr.write(sys.argv[0] + " : Replaying from file; stopping at last line (" + str(count) + ")\n")
			sys.stderr.write(sys.argv[0] + " : (You requested line " + str(self.max_lines) + ")\n")

		if self.end and isinstance(graphics, GraphicsThread):
			#graphics.stop()
			pass # Let the user stop the display
		elif not self.end:
			global game
			game = GameThread(self.board, self.players)
			game.run()
		

		

def opponent(colour):
	if colour == "white":
		return "black"
	else:
		return "white"
# --- game.py --- #
try:
	import pygame
except:
	pass
import os

# Dictionary that stores the unicode character representations of the different pieces
# Chess was clearly the reason why unicode was invented
# For some reason none of the pygame chess implementations I found used them!
piece_char = {"white" : {"king" : u'\u2654',
			 "queen" : u'\u2655',
			 "rook" : u'\u2656',
			 "bishop" : u'\u2657',
			 "knight" : u'\u2658',
			 "pawn" : u'\u2659',
			 "unknown" : '?'},
		"black" : {"king" : u'\u265A',
			 "queen" : u'\u265B',
			 "rook" : u'\u265C',
			 "bishop" : u'\u265D',
			 "knight" : u'\u265E',
			 "pawn" : u'\u265F',
			 "unknown" : '?'}}

images = {"white" : {}, "black" : {}}
small_images = {"white" : {}, "black" : {}}

def create_images(grid_sz, font_name=os.path.join(os.path.curdir, "data", "DejaVuSans.ttf")):

	# Get the font sizes
	l_size = 5*(grid_sz[0] / 8)
	s_size = 3*(grid_sz[0] / 8)

	for c in piece_char.keys():
		
		if c == "black":
			for p in piece_char[c].keys():
				images[c].update({p : pygame.font.Font(font_name, l_size).render(piece_char[c][p], True,(0,0,0))})
				small_images[c].update({p : pygame.font.Font(font_name, s_size).render(piece_char[c][p],True,(0,0,0))})		
		elif c == "white":
			for p in piece_char[c].keys():
				images[c].update({p : pygame.font.Font(font_name, l_size+1).render(piece_char["black"][p], True,(255,255,255))})
				images[c][p].blit(pygame.font.Font(font_name, l_size).render(piece_char[c][p], True,(0,0,0)),(0,0))
				small_images[c].update({p : pygame.font.Font(font_name, s_size+1).render(piece_char["black"][p],True,(255,255,255))})
				small_images[c][p].blit(pygame.font.Font(font_name, s_size).render(piece_char[c][p],True,(0,0,0)),(0,0))
	

def load_images(image_dir=os.path.join(os.path.curdir, "data", "images")):
	if not os.path.exists(image_dir):
		raise Exception("Couldn't load images from " + image_dir + " (path doesn't exist)")
	for c in piece_char.keys():
		for p in piece_char[c].keys():
			images[c].update({p : pygame.image.load(os.path.join(image_dir, c + "_" + p + ".png"))})
			small_images[c].update({p : pygame.image.load(os.path.join(image_dir, c + "_" + p + "_small.png"))})
# --- images.py --- #
graphics_enabled = True
try:
	import pygame
except:
	graphics_enabled = False
	



# A thread to make things pretty
class GraphicsThread(StoppableThread):
	def __init__(self, board, title = "UCC::Progcomp 2013 - QChess", grid_sz = [80,80]):
		StoppableThread.__init__(self)
		
		self.board = board
		pygame.init()
		self.window = pygame.display.set_mode((grid_sz[0] * w, grid_sz[1] * h))
		pygame.display.set_caption(title)

		#print "Initialised properly"
		
		self.grid_sz = grid_sz[:]
		self.state = {"select" : None, "dest" : None, "moves" : None, "overlay" : None, "coverage" : None}
		self.error = 0
		self.lock = threading.RLock()
		self.cond = threading.Condition()

		#print "Test font"
		pygame.font.Font(os.path.join(os.path.curdir, "data", "DejaVuSans.ttf"), 32).render("Hello", True,(0,0,0))

		#load_images()
		create_images(grid_sz)

		"""
		for c in images.keys():
			for p in images[c].keys():
				images[c][p] = images[c][p].convert(self.window)
				small_images[c][p] = small_images[c][p].convert(self.window)
		"""

		
	


	# On the run from the world
	def run(self):
		
		while not self.stopped():
			
			#print "Display grid"
			self.board.display_grid(window = self.window, grid_sz = self.grid_sz) # Draw the board

			#print "Display overlay"
			self.overlay()

			#print "Display pieces"
			self.board.display_pieces(window = self.window, grid_sz = self.grid_sz) # Draw the board		

			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					if isinstance(game, GameThread):
						with game.lock:
							game.final_result = ""
							if game.state["turn"] != None:
								game.final_result = game.state["turn"].colour + " "
							game.final_result += "terminated"
						game.stop()
					self.stop()
					break
				elif event.type == pygame.MOUSEBUTTONDOWN:
					self.mouse_down(event)
				elif event.type == pygame.MOUSEBUTTONUP:
					self.mouse_up(event)
					

				
								
						
						
		self.message("Game ends, result \""+str(game.final_result) + "\"")
		time.sleep(1)

		# Wake up anyone who is sleeping
		self.cond.acquire()
		self.cond.notify()
		self.cond.release()

		pygame.quit() # Time to say goodbye

	# Mouse release event handler
	def mouse_up(self, event):
		if event.button == 3:
			with self.lock:
				self.state["overlay"] = None
		elif event.button == 2:
			with self.lock:
				self.state["coverage"] = None	

	# Mouse click event handler
	def mouse_down(self, event):
		if event.button == 1:
			m = [event.pos[i] / self.grid_sz[i] for i in range(2)]
			if isinstance(game, GameThread):
				with game.lock:
					p = game.state["turn"]
			else:
					p = None
					
					
			if isinstance(p, HumanPlayer):
				with self.lock:
					s = self.board.grid[m[0]][m[1]]
					select = self.state["select"]
				if select == None:
					if s != None and s.colour != p.colour:
						self.message("Wrong colour") # Look at all this user friendliness!
						time.sleep(1)
						return
					# Notify human player of move
					self.cond.acquire()
					with self.lock:
						self.state["select"] = s
						self.state["dest"] = None
					self.cond.notify()
					self.cond.release()
					return

				if select == None:
					return
						
					
				if self.state["moves"] == None:
					return

				if not m in self.state["moves"]:
					self.message("Illegal Move") # I still think last year's mouse interface was adequate
					time.sleep(2)
					return
						
				with self.lock:
					if self.state["dest"] == None:
						self.cond.acquire()
						self.state["dest"] = m
						self.state["select"] = None
						self.state["moves"] = None
						self.cond.notify()
						self.cond.release()
		elif event.button == 3:
			m = [event.pos[i] / self.grid_sz[i] for i in range(len(event.pos))]
			if isinstance(game, GameThread):
				with game.lock:
					p = game.state["turn"]
			else:
				p = None
					
					
			if isinstance(p, HumanPlayer):
				with self.lock:
					self.state["overlay"] = self.board.probability_grid(self.board.grid[m[0]][m[1]])

		elif event.button == 2:
			m = [event.pos[i] / self.grid_sz[i] for i in range(len(event.pos))]
			if isinstance(game, GameThread):
				with game.lock:
					p = game.state["turn"]
			else:
				p = None
			
			
			if isinstance(p, HumanPlayer):
				with self.lock:
					self.state["coverage"] = self.board.coverage(m[0], m[1], None, self.state["select"])
				
	# Draw the overlay
	def overlay(self):

		square_img = pygame.Surface((self.grid_sz[0], self.grid_sz[1]),pygame.SRCALPHA) # A square image
		# Draw square over the selected piece
		with self.lock:
			select = self.state["select"]
		if select != None:
			mp = [self.grid_sz[i] * [select.x, select.y][i] for i in range(len(self.grid_sz))]
			square_img.fill(pygame.Color(0,255,0,64))
			self.window.blit(square_img, mp)
		# If a piece is selected, draw all reachable squares
		# (This quality user interface has been patented)
		with self.lock:
			m = self.state["moves"]
		if m != None:
			square_img.fill(pygame.Color(255,0,0,128)) # Draw them in blood red
			for move in m:
				mp = [self.grid_sz[i] * move[i] for i in range(2)]
				self.window.blit(square_img, mp)
		# If a piece is overlayed, show all squares that it has a probability to reach
		with self.lock:
			m = self.state["overlay"]
		if m != None:
			for x in range(w):
				for y in range(h):
					if m[x][y] > 0.0:
						mp = [self.grid_sz[i] * [x,y][i] for i in range(2)]
						square_img.fill(pygame.Color(255,0,255,int(m[x][y] * 128))) # Draw in purple
						self.window.blit(square_img, mp)
						font = pygame.font.Font(os.path.join(os.path.curdir, "data", "DejaVuSans.ttf"), 14)
						text = font.render("{0:.2f}".format(round(m[x][y],2)), 1, pygame.Color(0,0,0))
						self.window.blit(text, mp)
				
		# If a square is selected, highlight all pieces that have a probability to reach it
		with self.lock:				
			m = self.state["coverage"]
		if m != None:
			for p in m:
				mp = [self.grid_sz[i] * [p.x,p.y][i] for i in range(2)]
				square_img.fill(pygame.Color(0,255,255, int(m[p] * 196))) # Draw in pale blue
				self.window.blit(square_img, mp)
				font = pygame.font.Font(os.path.join(os.path.curdir, "data", "DejaVuSans.ttf"), 14)
				text = font.render("{0:.2f}".format(round(m[p],2)), 1, pygame.Color(0,0,0))
				self.window.blit(text, mp)
			# Draw a square where the mouse is
		# This also serves to indicate who's turn it is
		
		if isinstance(game, GameThread):
			with game.lock:
				turn = game.state["turn"]
		else:
			turn = None

		if isinstance(turn, HumanPlayer):
			mp = [self.grid_sz[i] * int(pygame.mouse.get_pos()[i] / self.grid_sz[i]) for i in range(2)]
			square_img.fill(pygame.Color(0,0,255,128))
			if turn.colour == "white":
				c = pygame.Color(255,255,255)
			else:
				c = pygame.Color(0,0,0)
			pygame.draw.rect(square_img, c, (0,0,self.grid_sz[0], self.grid_sz[1]), self.grid_sz[0]/10)
			self.window.blit(square_img, mp)

	# Message in a bottle
	def message(self, string, pos = None, colour = None, font_size = 20):
		#print "Drawing message..."
		font = pygame.font.Font(os.path.join(os.path.curdir, "data", "DejaVuSans.ttf"), font_size)
		if colour == None:
			colour = pygame.Color(0,0,0)
		
		text = font.render(string, 1, colour)
	

		s = pygame.Surface((text.get_width(), text.get_height()), pygame.SRCALPHA)
		s.fill(pygame.Color(128,128,128))

		tmp = self.window.get_size()

		if pos == None:
			pos = (tmp[0] / 2 - text.get_width() / 2, tmp[1] / 3 - text.get_height())
		else:
			pos = (pos[0]*text.get_width() + tmp[0] / 2 - text.get_width() / 2, pos[1]*text.get_height() + tmp[1] / 3 - text.get_height())
		

		rect = (pos[0], pos[1], text.get_width(), text.get_height())
	
		pygame.draw.rect(self.window, pygame.Color(0,0,0), pygame.Rect(rect), 1)
		self.window.blit(s, pos)
		self.window.blit(text, pos)

		pygame.display.flip()

	def getstr(self, prompt = None):
		s = pygame.Surface((self.window.get_width(), self.window.get_height()))
		s.blit(self.window, (0,0))
		result = ""

		while True:
			#print "LOOP"
			if prompt != None:
				self.message(prompt)
				self.message(result, pos = (0, 1))
	
			pygame.event.pump()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return None
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_BACKSPACE:
						result = result[0:len(result)-1]
						self.window.blit(s, (0,0)) # Revert the display
						continue
				
						
					try:
						if event.unicode == '\r':
							return result
					
						result += str(event.unicode)
					except:
						continue


	# Function to pick a button
	def SelectButton(self, choices, prompt = None, font_size=20):

		#print "Select button called!"
		self.board.display_grid(self.window, self.grid_sz)
		if prompt != None:
			self.message(prompt)
		font = pygame.font.Font(os.path.join(os.path.curdir, "data", "DejaVuSans.ttf"), font_size)
		targets = []
		sz = self.window.get_size()

		
		for i in range(len(choices)):
			c = choices[i]
			
			text = font.render(c, 1, pygame.Color(0,0,0))
			p = (sz[0] / 2 - (1.5*text.get_width())/2, sz[1] / 2 +(i-1)*text.get_height()+(i*2))
			targets.append((p[0], p[1], p[0] + 1.5*text.get_width(), p[1] + text.get_height()))

		while True:
			mp =pygame.mouse.get_pos()
			for i in range(len(choices)):
				c = choices[i]
				if mp[0] > targets[i][0] and mp[0] < targets[i][2] and mp[1] > targets[i][1] and mp[1] < targets[i][3]:
					font_colour = pygame.Color(255,0,0)
					box_colour = pygame.Color(0,0,255,128)
				else:
					font_colour = pygame.Color(0,0,0)
					box_colour = pygame.Color(128,128,128)
				
				text = font.render(c, 1, font_colour)
				s = pygame.Surface((text.get_width()*1.5, text.get_height()), pygame.SRCALPHA)
				s.fill(box_colour)
				pygame.draw.rect(s, (0,0,0), (0,0,1.5*text.get_width(), text.get_height()), self.grid_sz[0]/10)
				s.blit(text, ((text.get_width()*1.5)/2 - text.get_width()/2 ,0))
				self.window.blit(s, targets[i][0:2])
				
	
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return None
				elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
					for i in range(len(targets)):
						t = targets[i]
						if event.pos[0] > t[0] and event.pos[0] < t[2]:
							if event.pos[1] > t[1] and event.pos[1] < t[3]:
								return i
						#print "Reject " + str(i) + str(event.pos) + " vs " + str(t)
		

	# Function to pick players in a nice GUI way
	def SelectPlayers(self, players = []):


		#print "SelectPlayers called"
		
		missing = ["white", "black"]
		for p in players:
			missing.remove(p.colour)

		for colour in missing:
			
			
			choice = self.SelectButton(["human", "agent", "network"],prompt = "Choose " + str(colour) + " player")
			if choice == 0:
				players.append(HumanPlayer("human", colour))
			elif choice == 1:
				import inspect
				internal_agents = inspect.getmembers(sys.modules[__name__], inspect.isclass)
				internal_agents = [x for x in internal_agents if issubclass(x[1], InternalAgent)]
				internal_agents.remove(('InternalAgent', InternalAgent)) 
				if len(internal_agents) > 0:
					choice2 = self.SelectButton(["internal", "external"], prompt="Type of agent")
				else:
					choice2 = 1

				if choice2 == 0:
					agent = internal_agents[self.SelectButton(map(lambda e : e[0], internal_agents), prompt="Choose internal agent")]
					players.append(agent[1](agent[0], colour))					
				elif choice2 == 1:
					try:
						import Tkinter
						from tkFileDialog import askopenfilename
						root = Tkinter.Tk() # Need a root to make Tkinter behave
						root.withdraw() # Some sort of magic incantation
						path = askopenfilename(parent=root, initialdir="../agents",title=
'Choose an agent.')
						if path == "":
							return self.SelectPlayers()
						players.append(make_player(path, colour))	
					except:
						
						p = None
						while p == None:
							self.board.display_grid(self.window, self.grid_sz)
							pygame.display.flip()
							path = self.getstr(prompt = "Enter path:")
							if path == None:
								return None
	
							if path == "":
								return self.SelectPlayers()
	
							try:
								p = make_player(path, colour)
							except:
								self.board.display_grid(self.window, self.grid_sz)
								pygame.display.flip()
								self.message("Invalid path!")
								time.sleep(1)
								p = None
						players.append(p)
			elif choice == 2:
				address = ""
				while address == "":
					self.board.display_grid(self.window, self.grid_sz)
					
					address = self.getstr(prompt = "Address? (leave blank for server)")
					if address == None:
						return None
					if address == "":
						address = None
						continue
					try:
						map(int, address.split("."))
					except:
						self.board.display_grid(self.window, self.grid_sz)
						self.message("Invalid IPv4 address!")
						address = ""

				players.append(NetworkReceiver(colour, address))
			else:
				return None
		#print str(self) + ".SelectPlayers returns " + str(players)
		return players
			
				
			
# --- graphics.py --- #
#!/usr/bin/python -u

# Do you know what the -u does? It unbuffers stdin and stdout
# I can't remember why, but last year things broke without that

"""
	UCC::Progcomp 2013 Quantum Chess game
	@author Sam Moore [SZM] "matches"
	@copyright The University Computer Club, Incorporated
		(ie: You can copy it for not for profit purposes)
"""

# system python modules or whatever they are called
import sys
import os
import time

turn_delay = 0.5
[game, graphics] = [None, None]

def make_player(name, colour):
	if name[0] == '@':
		if name[1:] == "human":
			return HumanPlayer(name, colour)
		s = name[1:].split(":")
		if s[0] == "network":
			address = None
			if len(s) > 1:
				address = s[1]
			return NetworkReceiver(colour, address)
		if s[0] == "internal":

			import inspect
			internal_agents = inspect.getmembers(sys.modules[__name__], inspect.isclass)
			internal_agents = [x for x in internal_agents if issubclass(x[1], InternalAgent)]
			internal_agents.remove(('InternalAgent', InternalAgent)) 
			
			if len(s) != 2:
				sys.stderr.write(sys.argv[0] + " : '@internal' should be followed by ':' and an agent name\n")
				sys.stderr.write(sys.argv[0] + " : Choices are: " + str(map(lambda e : e[0], internal_agents)) + "\n")
				return None

			for a in internal_agents:
				if s[1] == a[0]:
					return a[1](name, colour)
			
			sys.stderr.write(sys.argv[0] + " : Can't find an internal agent matching \"" + s[1] + "\"\n")
			sys.stderr.write(sys.argv[0] + " : Choices are: " + str(map(lambda e : e[0], internal_agents)) + "\n")
			return None
			

	else:
		return ExternalAgent(name, colour)
			


# The main function! It does the main stuff!
def main(argv):

	# Apparently python will silently treat things as local unless you do this
	# Anyone who says "You should never use a global variable" can die in a fire
	global game
	global graphics
	
	global turn_delay
	global agent_timeout
	global log_file
	global src_file
	global graphics_enabled
	global always_reveal_states

	max_lines = None
	src_file = None
	
	style = "quantum"
	colour = "white"

	# Get the important warnings out of the way
	if platform.system() == "Windows":
		sys.stderr.write(sys.argv[0] + " : Warning - You are using " + platform.system() + "\n")
		if platform.release() == "Vista":
			sys.stderr.write(sys.argv[0] + " : God help you.\n")
	

	players = []
	i = 0
	while i < len(argv)-1:
		i += 1
		arg = argv[i]
		if arg[0] != '-':
			p = make_player(arg, colour)
			if not isinstance(p, Player):
				sys.stderr.write(sys.argv[0] + " : Fatal error creating " + colour + " player\n")
				return 100
			players.append(p)
			if colour == "white":
				colour = "black"
			elif colour == "black":
				pass
			else:
				sys.stderr.write(sys.argv[0] + " : Too many players (max 2)\n")
			continue

		# Option parsing goes here
		if arg[1] == '-' and arg[2:] == "classical":
			style = "classical"
		elif arg[1] == '-' and arg[2:] == "quantum":
			style = "quantum"
		elif arg[1] == '-' and arg[2:] == "reveal":
			always_reveal_states = True
		elif (arg[1] == '-' and arg[2:] == "graphics"):
			graphics_enabled = not graphics_enabled
		elif (arg[1] == '-' and arg[2:].split("=")[0] == "file"):
			# Load game from file
			if len(arg[2:].split("=")) == 1:
				src_file = sys.stdin
			else:
				f = arg[2:].split("=")[1]
				if f[0] == '@':
					src_file = HttpReplay("http://" + f.split(":")[0][1:])
				else:
					src_file = open(f.split(":")[0], "r", 0)

				if len(f.split(":")) == 2:
					max_lines = int(f.split(":")[1])

		elif (arg[1] == '-' and arg[2:].split("=")[0] == "log"):
			# Log file
			if len(arg[2:].split("=")) == 1:
				log_file = LogFile(sys.stdout)
			else:
				f = arg[2:].split("=")[1]
				if f[0] == '@':
					log_file = HttpLog(f[1:])
				else:
					log_file = LogFile(open(f, "w", 0))
		elif (arg[1] == '-' and arg[2:].split("=")[0] == "delay"):
			# Delay
			if len(arg[2:].split("=")) == 1:
				turn_delay = 0
			else:
				turn_delay = float(arg[2:].split("=")[1])

		elif (arg[1] == '-' and arg[2:].split("=")[0] == "timeout"):
			# Timeout
			if len(arg[2:].split("=")) == 1:
				agent_timeout = -1
			else:
				agent_timeout = float(arg[2:].split("=")[1])
				
		elif (arg[1] == '-' and arg[2:] == "help"):
			# Help
			os.system("less data/help.txt") # The best help function
			return 0


	# Create the board
	
	# Construct a GameThread! Make it global! Damn the consequences!
			
	if src_file != None:
		# Hack to stop ReplayThread from exiting
		#if len(players) == 0:
		#	players = [HumanPlayer("dummy", "white"), HumanPlayer("dummy", "black")]

		# Normally the ReplayThread exits if there are no players
		# TODO: Decide which behaviour to use, and fix it
		end = (len(players) == 0)
		if end:
			players = [Player("dummy", "white"), Player("dummy", "black")]
		elif len(players) != 2:
			sys.stderr.write(sys.argv[0] + " : Usage " + sys.argv[0] + " white black\n")
			if graphics_enabled:
				sys.stderr.write(sys.argv[0] + " : (You won't get a GUI, because --file was used, and the author is lazy)\n")
			return 44
		game = ReplayThread(players, src_file, end=end, max_lines=max_lines)
	else:
		board = Board(style)
		game = GameThread(board, players) 



	# Initialise GUI
	if graphics_enabled == True:
		try:
			graphics = GraphicsThread(game.board, grid_sz = [64,64]) # Construct a GraphicsThread!

		except Exception,e:
			graphics = None
			sys.stderr.write(sys.argv[0] + " : Got exception trying to initialise graphics\n"+str(e.message)+"\nDisabled graphics\n")
			graphics_enabled = False

	# If there are no players listed, display a nice pretty menu
	if len(players) != 2:
		if graphics != None:
			players = graphics.SelectPlayers(players)
		else:
			sys.stderr.write(sys.argv[0] + " : Usage " + sys.argv[0] + " white black\n")
			return 44

	# If there are still no players, quit
	if players == None or len(players) != 2:
		sys.stderr.write(sys.argv[0] + " : Graphics window closed before players chosen\n")
		return 45


	# Wrap NetworkSender players around original players if necessary
	for i in range(len(players)):
		if isinstance(players[i], NetworkReceiver):
			players[i].board = board # Network players need direct access to the board
			for j in range(len(players)):
				if j == i:
					continue
				if isinstance(players[j], NetworkSender) or isinstance(players[j], NetworkReceiver):
					continue
				players[j] = NetworkSender(players[j], players[i].address)
				players[j].board = board

	# Connect the networked players
	for p in players:
		if isinstance(p, NetworkSender) or isinstance(p, NetworkReceiver):
			if graphics != None:
				graphics.board.display_grid(graphics.window, graphics.grid_sz)
				graphics.message("Connecting to " + p.colour + " player...")
			p.connect()

	
	# If using windows, select won't work; use horrible TimeoutPlayer hack
	if agent_timeout > 0:
		if platform.system() == "Windows":
			for i in range(len(players)):
				if isinstance(players[i], ExternalAgent) or isinstance(players[i], InternalAgent):
					players[i] = TimeoutPlayer(players[i], agent_timeout)

		else:
			warned = False
			# InternalAgents get wrapped to an ExternalAgent when there is a timeout
			# This is not confusing at all.
			for i in range(len(players)):
				if isinstance(players[i], InternalAgent):
						players[i] = ExternalWrapper(players[i])


		




	log_init(game.board, players)
	
	
	if graphics != None:
		game.start() # This runs in a new thread
		graphics.run()
		if game.is_alive():
			game.join()
	

		error = game.error + graphics.error
	else:
		game.run()
		error = game.error
	

	if log_file != None and log_file != sys.stdout:
		log_file.close()

	if src_file != None and src_file != sys.stdin:
		src_file.close()

	return error

# This is how python does a main() function...
if __name__ == "__main__":
	try:
		sys.exit(main(sys.argv))
	except KeyboardInterrupt:
		sys.stderr.write(sys.argv[0] + " : Got KeyboardInterrupt. Stopping everything\n")
		if isinstance(graphics, StoppableThread):
			graphics.stop()
			graphics.run() # Will clean up graphics because it is stopped, not run it (a bit dodgy)

		if isinstance(game, StoppableThread):
			game.stop()
			if game.is_alive():
				game.join()

		sys.exit(102)

# --- main.py --- #
# EOF - created from make on Wed Jan 30 19:45:59 WST 2013
