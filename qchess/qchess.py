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
		
		
		self.last_state = None
		
		self.move_pattern = None
		self.coverage = None
		self.possible_moves = {}
		

	def init_from_copy(self, c):
		self.colour = c.colour
		self.x = c.x
		self.y = c.y
		self.types = c.types[:]
		self.current_type = c.current_type
		self.choice = c.choice
		
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
			if always_reveal_states == True or self.types[i][0] != '?':
				if self.types[i][0] == '?':
					img = small_images[self.colour][self.types[i][1:]]
				else:
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
		if self.current_type == "unknown" or not self.choice in [0,1]:
			self.choice = random.randint(0,1)
			if self.types[self.choice][0] == '?':
				self.types[self.choice] = self.types[self.choice][1:]
			self.current_type = self.types[self.choice]
		return self.choice

	# Uncollapses (?) the wave function!
	def deselect(self):
		#print "Deselect called"
		if (self.x + self.y) % 2 != 0:
			if (self.types[0] != self.types[1]) or (self.types[0][0] == '?' or self.types[1][0] == '?'):
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
		self.max_moves = None
		self.moves = 0
		self.move_stack = []
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
					piece.types.append('?' + choice)
				elif style == "classical":
					piece.types.append(piece.types[0])
					piece.current_type = piece.types[0]
					piece.choice = 0

	def clone(self):
		newboard = Board(master = False)
		newpieces = newboard.pieces["white"] + newboard.pieces["black"]
		mypieces = self.pieces["white"] + self.pieces["black"]

		for i in range(len(mypieces)):
			newpieces[i].init_from_copy(mypieces[i])
	
	# Reset the board from a string
	def reset_board(self, s):
		self.pieces = {"white" : [], "black" : []}
		self.king = {"white" : None, "black" : None}
		self.grid = [[None] * w for _ in range(h)]
		for x in range(w):
			for y in range(h):
				self.grid[x][y] = None

		for line in s.split("\n"):
			if line == "":
				continue
			if line[0] == "#":
				continue

			tokens = line.split(" ")
			[x, y] = map(int, tokens[len(tokens)-1].split(","))
			current_type = tokens[1]
			types = map(lambda e : e.strip(" '[],"), line.split('[')[1].split(']')[0].split(','))
			
			target = Piece(tokens[0], x, y, types)
			target.current_type = current_type
			
			try:
				target.choice = types.index(current_type)
			except:
				target.choice = -1

			self.pieces[tokens[0]].append(target)
			if target.current_type == "king":
				self.king[tokens[0]] = target

			self.grid[x][y] = target
			

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
			raise Exception("BOUNDS " + str(x) + ","+str(y))

		piece = self.grid[x][y]
		if piece == None:
			raise Exception("EMPTY")

		if colour != None and piece.colour != colour:
			raise Exception("COLOUR " + str(piece.colour) + " not " + str(colour))

		# I'm not quite sure why I made this return a string, but screw logical design
		return str(x) + " " + str(y) + " " + str(piece.select()) + " " + str(piece.current_type)


	# Update the board when a piece has been selected
	# "type" is apparently reserved, so I'll use "state"
	def update_select(self, x, y, type_index, state, sanity=True, deselect=True):
		#debug(str(self) + " update_select called")
		piece = self.grid[x][y]
		if piece.types[type_index] == "unknown":
			if not state in self.unrevealed_types[piece.colour].keys() and sanity == True:
				raise Exception("SANITY: Too many " + piece.colour + " " + state + "s")
			self.unrevealed_types[piece.colour][state] -= 1
			if self.unrevealed_types[piece.colour][state] <= 0:
				del self.unrevealed_types[piece.colour][state]

		piece.types[type_index] = state
		piece.current_type = state

		if deselect == True and len(self.possible_moves(piece)) <= 0:
			piece.deselect() # Piece can't move; deselect it
			
		# Piece needs to recalculate moves
		piece.possible_moves = None
		
	# Update the board when a piece has been moved
	def update_move(self, x, y, x2, y2, sanity=True):
		#debug(str(self) + " update_move called \""+str(x)+ " " + str(y) + " -> " + str(x2) + " " + str(y2) + "\"")	
		piece = self.grid[x][y]
		#print "Moving " + str(x) + "," + str(y) + " to " + str(x2) + "," + str(y2) + "; possible_moves are " + str(self.possible_moves(piece))
		
		if not [x2,y2] in self.possible_moves(piece) and sanity == True:
			raise Exception("ILLEGAL move " + str(x2)+","+str(y2))
		
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
		self.moves += 1
		
		# All other pieces need to recalculate moves
		for p in self.pieces["white"] + self.pieces["black"]:
			p.possible_moves = None
		
		#self.verify()	

	# Update the board from a string
	# Guesses what to do based on the format of the string
	def update(self, result, sanity=True, deselect=True):
		#debug(str(self) + " update called \""+str(result)+"\"")
		# String always starts with 'x y'
		try:
			s = result.split(" ")
			[x,y] = map(int, s[0:2])	
		except:
			raise Exception("GIBBERISH \""+ str(result) + "\"") # Raise expectations

		piece = self.grid[x][y]
		if piece == None and sanity == True:
			raise Exception("EMPTY " + str(x) + " " + str(y))

		# If a piece is being moved, the third token is '->'
		# We could get away with just using four integers, but that wouldn't look as cool
		if "->" in s:
			# Last two tokens are the destination
			try:
				[x2,y2] = map(int, s[3:])
			except:
				raise Exception("GIBBERISH \"" + str(result) + "\"") # Raise the alarm

			# Move the piece (take opponent if possible)
			self.update_move(x, y, x2, y2, sanity)
			
		else:
			# Otherwise we will just assume a piece has been selected
			try:
				type_index = int(s[2]) # We need to know which of the two types the piece is in; that's the third token
				state = s[3] # The last token is a string identifying the type
			except:
				raise Exception("GIBBERISH \"" + result + "\"") # Throw a hissy fit


			# Select the piece
			self.update_select(x, y, type_index, state, sanity=sanity, deselect=deselect)

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
		
		#self.verify()
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
			prob = 1.0 / float(len(p.types))
			if t == "unknown" or p.types[i][0] == '?':
				total_types = 0
				for t2 in self.unrevealed_types[p.colour].keys():
					total_types += self.unrevealed_types[p.colour][t2]
				
				for t2 in self.unrevealed_types[p.colour].keys():
					prob2 = float(self.unrevealed_types[p.colour][t2]) / float(total_types)
					#p.current_type = t2
					for point in self.possible_moves(p, reject_allied, state=t2):
						result[point[0]][point[1]] += prob2 * prob
				
			else:
				#p.current_type = t
				for point in self.possible_moves(p, reject_allied, state=t):
						result[point[0]][point[1]] += prob
		
		#self.verify()
		#p.current_type = "unknown"
		return result

	def prob_is_type(self, p, state):
		if p.current_type != 0:
			if state == p.current_type:
				return 1.0
			else:
				return 0.0
		
		prob = 0.5
		result = 0
		for i in range(len(p.types)):
			t = p.types[i]
			if t == state:
				result += prob
				continue	
			if t == "unknown" or p.types[i][0] == '?':
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
	def possible_moves(self, p, reject_allied = True, state=None):
		if p == None:
			raise Exception("SANITY: No piece")
		
		
		
		if state != None and state != p.current_type:
			old_type = p.current_type
			p.current_type = state
			result = self.possible_moves(p, reject_allied, state=None)
			p.current_type = old_type
			return result
		
		
		
		
		result = []
		

		
		if p.current_type == "unknown":
			raise Exception("SANITY: Unknown state for piece: "+str(p))
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
		
		#self.verify()
		
		p.possible_moves = result
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

	# Returns "white", "black" or "DRAW" if the game should end
	def end_condition(self):
		if self.king["white"] == None:
			if self.king["black"] == None:
				return "DRAW" # This shouldn't happen
			return "black"
		elif self.king["black"] == None:
			return "white"
		elif len(self.pieces["white"]) == 1 and len(self.pieces["black"]) == 1:
			return "DRAW"
		elif self.max_moves != None and self.moves > self.max_moves:
			return "DRAW"
		return None


	# I typed the full statement about 30 times before writing this function...
	def on_board(self, x, y):
		return (x >= 0 and x < w) and (y >= 0 and y < h)
	
	
	
	# Pushes a move temporarily
	def push_move(self, piece, x, y):
		target = self.grid[x][y]
		self.move_stack.append([piece, target, piece.x, piece.y, x, y])
		[piece.x, piece.y] = [x, y]
		self.grid[x][y] = piece
		self.grid[piece.x][piece.y] = None
		
		for p in self.pieces["white"] + self.pieces["black"]:
			p.possible_moves = None
		
	# Restore move
	def pop_move(self):
		#print str(self.move_stack)
		[piece, target, x1, y1, x2, y2] = self.move_stack[len(self.move_stack)-1]
		self.move_stack = self.move_stack[:-1]
		piece.x = x1
		piece.y = y1
		self.grid[x1][y1] = piece
		if target != None:
			target.x = x2
			target.y = y2
		self.grid[x2][y2] = target
		
		for p in self.pieces["white"] + self.pieces["black"]:
			p.possible_moves = None
		
# --- board.py --- #
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
	
	def __str__(self):
		return self.name + "<"+str(self.colour)+">"

	def base_player(self):
		return self


	


def open_fifo(name, mode, timeout=None):
	if timeout == None:
		return open(name, mode)
	
	
	class Worker(threading.Thread):
		def __init__(self):
			threading.Thread.__init__(self)
			self.result = None
			self.exception = None

			
		def run(self):		
			try:
				self.result = open(name, mode)
			except Exception, e:
				self.exception = e
				self.result = None
		

	w = Worker()
	w.start()
	
	start = time.time()
	while time.time() - start < timeout:
		if w.is_alive() == False:
			w.join()
			if w.exception != None:
				raise w.exception
			return w.result
		time.sleep(0.1)
	
	
	if w.is_alive():
		#sys.stderr.write("FIFO_TIMEOUT!\n")
		# Recursive to deal with possible race condition
		try:
			if mode == "r":
				f = open_fifo(name, "w", 1)
			else:
				f = open_fifo(name, "r", 1)
		except:
			pass
			
		#sys.stderr.write("Opened other end!\n")
		while w.is_alive():
			time.sleep(0.1)
			
		w.join()
		f.close()
		w.result.close()
		raise Exception("FIFO_TIMEOUT")
	else:
		w.join()
		if w.exception != None:
			raise w.exception
		return w.result
	

# Player that runs through a fifo
class FifoPlayer(Player):
	
	timeout = 300
	
	def __init__(self, name, colour):
		Player.__init__(self, name, colour)
		os.mkfifo(self.name+".in")
		os.mkfifo(self.name+".out")
			

		try:
			self.fifo_out = open_fifo(self.name+".out","w", FifoPlayer.timeout)
		except:
			raise Exception("FIFO_TIMEOUT")
		else:
			self.fifo_out.write("START "+colour+"\n")
			self.fifo_out.close()

				
	def update(self, result):
		sys.stderr.write("update fifo called\n")
		try:
			self.fifo_out = open_fifo(self.name+".out", "w", FifoPlayer.timeout)
		except:
			raise Exception("FIFO_TIMEOUT")
		else:
			self.fifo_out.write(result +"\n")
			self.fifo_out.close()
			return result
		
	def select(self):
		sys.stderr.write("select fifo called\n")
		try:
			self.fifo_out = open_fifo(self.name+".out", "w", FifoPlayer.timeout)
		except:
			#sys.stderr.write("TIMEOUT\n")
			raise Exception("FIFO_TIMEOUT")
		else:
			
			self.fifo_out.write("SELECT?\n")
			self.fifo_out.close()
			self.fifo_in = open_fifo(self.name+".in", "r", FifoPlayer.timeout)
			s = map(int, self.fifo_in.readline().strip(" \r\n").split(" "))
			self.fifo_in.close()
			return s
	
	def get_move(self):
		sys.stderr.write("get_move fifo called\n")
		try:
			self.fifo_out = open_fifo(self.name+".out", "w", FifoPlayer.timeout)
		except:
			raise Exception("FIFO_TIMEOUT")
		else:
			self.fifo_out.write("MOVE?\n")
			self.fifo_out.close()
			self.fifo_in = open_fifo(self.name+".in", "r", FifoPlayer.timeout)
			s = map(int, self.fifo_in.readline().strip(" \r\n").split(" "))
			self.fifo_in.close()
			return s
	
	def quit(self, result):
		try:
			self.fifo_out = open_fifo(self.name+".out", "w", FifoPlayer.timeout)
		except:
			pass
		else:
			self.fifo_out.write(result + "\n")
			self.fifo_out.close()

		try:
			os.remove(self.name+".in")
			os.remove(self.name+".out")
		except OSError:
			pass

# Player that runs from another process
class ExternalAgent(Player):


	def __init__(self, name, colour):
		Player.__init__(self, name, colour)
		#raise Exception("waht")
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
					return p
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
					return p
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

	def argForm(self):
		return "@internal:"+self.name

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

	

# --- player.py --- #
# A sample agent


class AgentBishop(AgentRandom): # Inherits from AgentRandom (in qchess)
	def __init__(self, name, colour,value={"pawn" : 1, "bishop" : 3, "knight" : 3, "rook" : 5, "queen" : 9, "king" : 100, "unknown" : 2}):
		InternalAgent.__init__(self, name, colour)
		self.value = value
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
				self.board.push_move(piece, x, y)
				

				
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

				self.board.pop_move()
				

				
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
			return AgentRandom.get_move(self)

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
		#try:
		self.q.put(self.function(*self.args))
		#except IOError:
		#	pass
		
		

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
		time.sleep(0.1)
	
		

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

class NetworkPlayer(Player):
	def __init__(self, colour, network, player):
		Player.__init__(self, "@network:"+str(network.address), colour) 
		self.player = player
		self.network = network
		
	def __str__(self):
		return "NetworkPlayer<"+str(self.colour)+","+str(self.player)+">"
		
	def select(self):
		#debug(str(self) + " select called")
		if self.player != None:
			s = self.player.select()
			self.send_message(str(s[0]) + " " + str(s[1]))
		else:
			s = map(int, self.get_response().split(" "))
			for p in game.players:
				if p != self and isinstance(p, NetworkPlayer) and p.player == None:
					p.network.send_message(str(s[0]) + " " + str(s[1]))
		if s == [-1,-1]:
			game.final_result = "network terminate"
			game.stop()
		return s
	
	def send_message(self, message):
		#debug(str(self) + " send_message(\""+str(message)+"\") called")
		self.network.send_message(message)
		
	def get_response(self):
		#debug(str(self) + " get_response() called")
		s = self.network.get_response()
		#debug(str(self) + " get_response() returns \""+str(s)+"\"")
		return s
			
			
	def get_move(self):
		#debug(str(self) + " get_move called")
		if self.player != None:
			s = self.player.get_move()
			self.send_message(str(s[0]) + " " + str(s[1]))
		else:
			s = map(int, self.get_response().split(" "))
			for p in game.players:
				if p != self and isinstance(p, NetworkPlayer) and p.player == None:
					p.network.send_message(str(s[0]) + " " + str(s[1]))
					
		if s == [-1,-1]:
			game.final_result = "network terminate"
			game.stop()
		return s
	
	def update(self, result):
		#debug(str(self) + " update(\""+str(result)+"\") called")
		if self.network.server == True:
			if self.player == None:
				self.send_message(result)
		elif self.player != None:
			result = self.get_response()
			if result == "-1 -1":
				game.final_result = "network terminate"
				game.stop()
				return "-1 -1"
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
		try:
			self.send_message("-1 -1")
		except:
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
		#debug(str(self) + "Tries to connect")
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
			raise Exception("NET_UNRESPONSIVE")


		debug("Network get_response s = " + str(s))

		while s[len(s)-1] != '\n':
			# Timeout on each character in the message
			if network_timeout_delay > 0.0:
				ready = select.select([self.src], [], [], network_timeout_delay)[0]
			else:
				ready = [self.src]
			if self.src in ready:
				s += self.src.recv(1) 
			else:
				raise Exception("NET_UNRESPONSIVE")

		
		return s.strip(" \r\n")

	def send_message(self,s):
		if network_timeout_start > 0.0:
			ready = select.select([], [self.src], [], network_timeout_start)[1]
		else:
			ready = [self.src]

		if self.src in ready:
			self.src.send(s + "\n")
		else:
			raise Exception("NET_UNRESPONSIVE")
		
		

	def close(self):
		self.src.shutdown()
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
		return self._stop.isSet()# --- thread_util.py --- #
log_files = []
import datetime
import urllib2

class LogFile():
	def __init__(self, log, name):	
		self.name = name
		self.log = log
		self.logged = []
		self.log.write("# Log starts " + str(datetime.datetime.now()) + "\n")

	def write(self, s):
		now = datetime.datetime.now()
		self.log.write(str(now) + " : " + s + "\n")
		self.logged.append((now, s))

	def setup(self, board, players):
		
		for p in players:
			self.log.write("# " + str(p.colour) + " : " + str(p.name) + "\n")
		
		self.log.write("# Initial board\n")
		for x in range(0, w):
			for y in range(0, h):
				if board.grid[x][y] != None:
					self.log.write(str(board.grid[x][y]) + "\n")

		self.log.write("# Start game\n")

	def close(self):
		self.log.write("# EOF\n")
		if self.log != sys.stdout:
			self.log.close()

class ShortLog(LogFile):
	def __init__(self, file_name):
		if file_name == "":
			self.log = sys.stdout
		else:
			self.log = open(file_name, "w", 0)
		LogFile.__init__(self, self.log, "@"+file_name)
		self.file_name = file_name
		self.phase = 0

	def write(self, s):
		now = datetime.datetime.now()
		self.logged.append((now, s))
		
		if self.phase == 0:
			if self.log != sys.stdout:
				self.log.close()
				self.log = open(self.file_name, "w", 0)
			self.log.write("# Short log updated " + str(datetime.datetime.now()) + "\n")	
			LogFile.setup(self, game.board, game.players)

		elif self.phase == 1:
			for message in self.logged[len(self.logged)-2:]:
				self.log.write(str(message[0]) + " : " + message[1] + "\n")

		self.phase = (self.phase + 1) % 2		
		
	def close(self):
		if self.phase == 1:
			ending = self.logged[len(self.logged)-1]
			self.log.write(str(ending[0]) + " : " + ending[1] + "\n")
		self.log.write("# EOF\n")
		if self.log != sys.stdout:
			self.log.close()
		

class HeadRequest(urllib2.Request):
	def get_method(self):
		return "HEAD"

class HttpGetter(StoppableThread):
	def __init__(self, address):
		StoppableThread.__init__(self)
		self.address = address
		self.log = urllib2.urlopen(address)
		self.lines = []
		self.lock = threading.RLock() #lock for access of self.state
		self.cond = threading.Condition() # conditional

	def run(self):
		while not self.stopped():
			line = self.log.readline()
			if line == "":
				date_mod = datetime.datetime.strptime(self.log.headers['last-modified'], "%a, %d %b %Y %H:%M:%S GMT")
				self.log.close()
	
				next_log = urllib2.urlopen(HeadRequest(self.address))
				date_new = datetime.datetime.strptime(next_log.headers['last-modified'], "%a, %d %b %Y %H:%M:%S GMT")
				while date_new <= date_mod and not self.stopped():
					next_log = urllib2.urlopen(HeadRequest(self.address))
					date_new = datetime.datetime.strptime(next_log.headers['last-modified'], "%a, %d %b %Y %H:%M:%S GMT")
				if self.stopped():
					break

				self.log = urllib2.urlopen(self.address)
				line = self.log.readline()

			self.cond.acquire()
			self.lines.append(line)
			self.cond.notifyAll()
			self.cond.release()

			#sys.stderr.write(" HttpGetter got \'" + str(line) + "\'\n")

		self.log.close()
				
				
	
		
		
class HttpReplay():
	def __init__(self, address):
		self.getter = HttpGetter(address)
		self.getter.start()
		
	def readline(self):
		self.getter.cond.acquire()
		while len(self.getter.lines) == 0:
			self.getter.cond.wait()
			
		result = self.getter.lines[0]
		self.getter.lines = self.getter.lines[1:]
		self.getter.cond.release()

		return result
			
			
	def close(self):
		self.getter.stop()

class FileReplay():
	def __init__(self, filename):
		self.f = open(filename, "r", 0)
		self.filename = filename
		self.mod = os.path.getmtime(filename)
		self.count = 0
	
	def readline(self):
		line = self.f.readline()
		
		while line == "":
			mod2 = os.path.getmtime(self.filename)
			if mod2 > self.mod:
				#sys.stderr.write("File changed!\n")
				self.mod = mod2
				self.f.close()
				self.f = open(self.filename, "r", 0)
				
				new_line = self.f.readline()
				
				if " ".join(new_line.split(" ")[0:3]) != "# Short log":
					for i in range(self.count):
						new_line = self.f.readline()
						#sys.stderr.write("Read back " + str(i) + ": " + str(new_line) + "\n")
					new_line = self.f.readline()
				else:
					self.count = 0
				
				line = new_line

		self.count += 1
		return line

	def close(self):
		self.f.close()
		
						
def log(s):
	for l in log_files:
		l.write(s)
		
def debug(s):
	sys.stderr.write("# DEBUG: " + s + "\n")
		

def log_init(board, players):
	for l in log_files:
		l.setup(board, players)

# --- log.py --- #



	

# A thread that runs the game
class GameThread(StoppableThread):
	def __init__(self, board, players, server = True):
		StoppableThread.__init__(self)
		self.board = board
		self.players = players
		self.state = {"turn" : None} # The game state
		self.error = 0 # Whether the thread exits with an error
		self.lock = threading.RLock() #lock for access of self.state
		self.cond = threading.Condition() # conditional for some reason, I forgot
		self.final_result = ""
		self.server = server
		self.retry_illegal = False
		
		
	

	# Run the game (run in new thread with start(), run in current thread with run())
	def run(self):
		result = ""
		while not self.stopped():
			
			for p in self.players:
				with self.lock:
					self.state["turn"] = p.base_player()
				try:
				#if True:
					[x,y] = p.select() # Player selects a square
					if self.stopped():
						#debug("Quitting in select")
						break
						
					if isinstance(p, NetworkPlayer):
						if p.network.server == True:
							result = self.board.select(x, y, colour = p.colour)
						else:
							result = None
							
					else:
						result = self.board.select(x, y, colour = p.colour)
					
					result = p.update(result)
					if self.stopped():
						break
					for p2 in self.players:
						if p2 == p:
							continue
						p2.update(result) # Inform players of what happened
						if self.stopped():
							break
					
					if self.stopped():
						break


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

					#try:
					[x2,y2] = p.get_move() # Player selects a destination
					#except:
					#	self.stop()

					if self.stopped():
						#debug("Quitting in get_move")
						break
					
					if isinstance(p, NetworkPlayer):
						if p.network.server == True:
							result = str(x) + " " + str(y) + " -> " + str(x2) + " " + str(y2)
							self.board.update_move(x, y, x2, y2)
						else:
							result = None
							
					else:
						result = str(x) + " " + str(y) + " -> " + str(x2) + " " + str(y2)
						self.board.update_move(x, y, x2, y2)
					
					result = p.update(result)
					if self.stopped():
						break
					for p2 in self.players:
						if p2 == p:
							continue
						p2.update(result) # Inform players of what happened
						if self.stopped():
							break
					
					if self.stopped():
						break
					
					
											
					log(result)


										

					if isinstance(graphics, GraphicsThread):
						with graphics.lock:
							graphics.state["moves"] = [[x2,y2]]

					time.sleep(turn_delay)

					if isinstance(graphics, GraphicsThread):
						with graphics.lock:
							graphics.state["select"] = None
							graphics.state["dest"] = None
							graphics.state["moves"] = None

			
					end = self.board.end_condition()
					if end != None:		
						with self.lock:
							if end == "DRAW":
								self.final_result = self.state["turn"].colour + " " + end
							else:
								self.final_result = end
						self.stop()
				
					if self.stopped():
						break
				except Exception,e:
				#if False:

					
					result = e.message
					if self.retry_illegal:
						self.state["turn"].update(result);
					else:
						sys.stderr.write("qchess.py exception: "+result + "\n")
						self.stop()
						with self.lock:
							self.final_result = self.state["turn"].colour + " " + e.message
						break



		for p2 in self.players:
			p2.quit(self.final_result)

		log(self.final_result)

		if isinstance(graphics, GraphicsThread):
			graphics.stop()

	
# A thread that replays a log file
class ReplayThread(GameThread):
	def __init__(self, players, src, end=False,max_moves=None):
		self.board = Board(style="empty")
		self.board.max_moves = max_moves
		GameThread.__init__(self, self.board, players)
		self.src = src
		self.end = end

		self.reset_board(self.src.readline())

	def reset_board(self, line):
		agent_str = ""
		self_str = ""
		while line != "# Start game" and line != "# EOF":
			
			while line == "":
				line = self.src.readline().strip(" \r\n")
				continue

			if line[0] == '#':
				line = self.src.readline().strip(" \r\n")
				continue

			self_str += line + "\n"

			if self.players[0].name == "dummy" and self.players[1].name == "dummy":
				line = self.src.readline().strip(" \r\n")
				continue
			
			tokens = line.split(" ")
			types = map(lambda e : e.strip("[] ,'"), tokens[2:4])
			for i in range(len(types)):
				if types[i][0] == "?":
					types[i] = "unknown"

			agent_str += tokens[0] + " " + tokens[1] + " " + str(types) + " ".join(tokens[4:]) + "\n"
			line = self.src.readline().strip(" \r\n")

		for p in self.players:
			p.reset_board(agent_str)
		
		
		self.board.reset_board(self_str)

	
	def run(self):
		move_count = 0
		last_line = ""
		line = self.src.readline().strip(" \r\n")
		while line != "# EOF":


			if self.stopped():
				break
			
			if len(line) <= 0:
				continue
					

			if line[0] == '#':
				last_line = line
				line = self.src.readline().strip(" \r\n")
				continue

			tokens = line.split(" ")
			if tokens[0] == "white" or tokens[0] == "black":
				self.reset_board(line)
				last_line = line
				line = self.src.readline().strip(" \r\n")
				continue

			move = line.split(":")
			move = move[len(move)-1].strip(" \r\n")
			tokens = move.split(" ")
			
			
			try:
				[x,y] = map(int, tokens[0:2])
			except:
				last_line = line
				self.stop()
				break

			log(move)

			target = self.board.grid[x][y]
			with self.lock:
				if target.colour == "white":
					self.state["turn"] = self.players[0]
				else:
					self.state["turn"] = self.players[1]
			
			move_piece = (tokens[2] == "->")
			if move_piece:
				[x2,y2] = map(int, tokens[len(tokens)-2:])

			if isinstance(graphics, GraphicsThread):
				with graphics.lock:
					graphics.state["select"] = target
					
			if not move_piece:
				self.board.update_select(x, y, int(tokens[2]), tokens[len(tokens)-1])
				if isinstance(graphics, GraphicsThread):
					with graphics.lock:
						if target.current_type != "unknown":
							graphics.state["moves"] = self.board.possible_moves(target)
						else:
							graphics.state["moves"] = None
					time.sleep(turn_delay)
			else:
				self.board.update_move(x, y, x2, y2)
				if isinstance(graphics, GraphicsThread):
					with graphics.lock:
						graphics.state["moves"] = [[x2,y2]]
					time.sleep(turn_delay)
					with graphics.lock:
						graphics.state["select"] = None
						graphics.state["moves"] = None
						graphics.state["dest"] = None
			

			
			
			
			for p in self.players:
				p.update(move)

			last_line = line
			line = self.src.readline().strip(" \r\n")
			
			
			end = self.board.end_condition()
			if end != None:
				self.final_result = end
				self.stop()
				break
					
						
						

			
					


			

				
			

		

		if self.end and isinstance(graphics, GraphicsThread):
			#graphics.stop()
			pass # Let the user stop the display
		elif not self.end and self.board.end_condition() == None:
			global game
			# Work out the last move
					
			t = last_line.split(" ")
			if t[len(t)-2] == "black":
				self.players.reverse()
			elif t[len(t)-2] == "white":
				pass
			elif self.state["turn"] != None and self.state["turn"].colour == "white":
				self.players.reverse()


			game = GameThread(self.board, self.players)
			game.run()
		else:
			pass

		

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
	os.environ["SDL_VIDEO_ALLOW_SCREENSAVER"] = "1"
except:
	graphics_enabled = False
	
import time



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
		self.sleep_timeout = None
		self.last_event = time.time()
		self.blackout = False

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
			
			if self.sleep_timeout == None or (time.time() - self.last_event) < self.sleep_timeout:
			
				#print "Display grid"
				self.board.display_grid(window = self.window, grid_sz = self.grid_sz) # Draw the board

				#print "Display overlay"
				self.overlay()

				#print "Display pieces"
				self.board.display_pieces(window = self.window, grid_sz = self.grid_sz) # Draw the board		
				self.blackout = False
				
			elif pygame.mouse.get_focused() and not self.blackout:
				os.system("xset dpms force off")
				self.blackout = True
				self.window.fill((0,0,0))

			pygame.display.flip()

			for event in pygame.event.get():
				self.last_event = time.time()
				if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
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
		

	# Function to choose between dedicated server or normal play
	def SelectServer(self):
	
		choice = self.SelectButton(["Normal", "Join Eigenserver"],prompt="Game type?")
		if choice == 0:
			return None
		choice = self.SelectButton(["progcomp.ucc", "other"], prompt="Address?")
		if choice == 0:
			return "progcomp.ucc.asn.au"
		else:
			return self.getstr(prompt = "Enter address:")
			
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
			elif choice == 1:
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
def dedicated_server():
	global log_files
	
	max_games = 5
	games = []
	gameID = 0
	while True:
		# Get players
		gameID += 1
		log("Getting clients...")
		s = socket.socket()
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(("0.0.0.0", 4562))
		s.listen(2)
		ss = s.accept()
		
		log("Got white player")
		
		args = ["python", "qchess.py", "--no-graphics", "@network::"+str(4600+2*len(games)), "@network::"+str(4600+2*len(games))]
		if len(log_files) != 0:
			for l in log_files:
				if l.name == "":
					args.append("--log")
				else:
					args.append("--log="+str(l.name)+"_"+str(gameID))
		
		g = subprocess.Popen(args, stdout=subprocess.PIPE)
		games.append(g)
		
		time.sleep(0.5)
		ss[0].send("white " + str(4600 + 2*(len(games)-1)))
		ss[0].shutdown(socket.SHUT_RD)
		ss[0].close()
		
		time.sleep(0.5)
		ss = s.accept()
		
		log("Got black player")
		
		time.sleep(0.5)
		ss[0].send("black " + str(4600 + 2*(len(games)-1)))
		ss[0].shutdown(socket.SHUT_RD)
		ss[0].close()
		
		s.shutdown(socket.SHUT_RDWR)
		s.close()
		
		
		while len(games) > max_games:
			#log("Too many games; waiting for game to finish...")
			ready = select.select(map(lambda e : e.stdout, games),[], [])
			for r in ready[0]:
				s = r.readline().strip(" \r\n").split(" ")
				if s[0] == "white" or s[0] == "black":
					for g in games[:]:
						if g.stdout == r:
							log("Game " + str(g) + " has finished")
							games.remove(g)
							
	return 0
	
def client(addr, player="@human"):
	
	
	debug("Client " + player + " starts")
	s = socket.socket()
	s.connect((addr, 4562))
	
	[colour,port] = s.recv(1024).strip(" \r\n").split(" ")
	
	debug("Colour: " + colour + ", port: " + port)
	
	s.shutdown(socket.SHUT_RDWR)
	s.close()
	
	if colour == "white":
		p = subprocess.Popen(["python", "qchess.py", player, "@network:"+addr+":"+port])
	else:
		p = subprocess.Popen(["python", "qchess.py", "@network:"+addr+":"+port, player])
	p.wait()
	return 0
# --- server.py --- #
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
sleep_timeout = None
[game, graphics] = [None, None]

def make_player(name, colour):
	debug(name)
	if name[0] == '@':
		if name[1:] == "human":
			return HumanPlayer(name, colour)
		s = name[1:].split(":")
		if s[0] == "network":
			ip = None
			port = 4562
			#print str(s)
			if len(s) > 1:
				if s[1] != "":
					ip = s[1]
			if len(s) > 2:
				port = int(s[2])
				
			if ip == None:
				if colour == "black":
					port += 1
			elif colour == "white":
				port += 1
						
			return NetworkPlayer(colour, Network((ip, port)), None)
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
		if s[0] == "fifo":
			if len(s) > 1:
				return FifoPlayer(s[1], colour)
			else:
				return FifoPlayer(str(os.getpid())+"."+colour, colour)

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
	global log_files
	global src_file
	global graphics_enabled
	global always_reveal_states
	global sleep_timeout


	retry_illegal = False
	server_addr = None

	max_moves = None
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
			players.append(arg)
			continue

		# Option parsing goes here
		if arg[1] == '-' and arg[2:] == "classical":
			style = "classical"
		elif arg[1] == '-' and arg[2:] == "quantum":
			style = "quantum"
		elif arg[1] == '-' and arg[2:] == "reveal":
			always_reveal_states = True
		elif (arg[1] == '-' and arg[2:] == "graphics"):
			graphics_enabled = True
		elif (arg[1] == '-' and arg[2:] == "no-graphics"):
			graphics_enabled = False
		elif (arg[1] == '-' and arg[2:].split("=")[0] == "file"):
			# Load game from file
			if len(arg[2:].split("=")) == 1:
				src_file = sys.stdin
			else:
				f = arg[2:].split("=")[1]
				if f[0:7] == "http://":
					src_file = HttpReplay(f)
				else:
					src_file = FileReplay(f.split(":")[0])

					if len(f.split(":")) == 2:
						max_moves = int(f.split(":")[1])
						
		elif (arg[1] == '-' and arg[2:].split("=")[0] == "server"):
			#debug("Server: " + str(arg[2:]))
			if len(arg[2:].split("=")) <= 1:
				server_addr = True
			else:
				server_addr = arg[2:].split("=")[1]
			
		elif (arg[1] == '-' and arg[2:].split("=")[0] == "log"):
			# Log file
			if len(arg[2:].split("=")) == 1:
				log_files.append(LogFile(sys.stdout,""))
			else:
				f = arg[2:].split("=")[1]
				if f == "":
					log_files.append(LogFile(sys.stdout, ""))
				elif f[0] == '@':
					log_files.append(ShortLog(f[1:]))
				else:
					log_files.append(LogFile(open(f, "w", 0), f))
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
		elif (arg[1] == '-' and arg[2:].split("=")[0] == "blackout"):
			# Screen saver delay
			if len(arg[2:].split("=")) == 1:
				sleep_timeout = -1
			else:
				sleep_timeout = float(arg[2:].split("=")[1])
		elif (arg[1] == '-' and arg[2:] == "retry-illegal"):
			retry_illegal = not retry_illegal
		elif (arg[1] == '-' and arg[2:] == "help"):
			# Help
			os.system("less data/help.txt") # The best help function
			return 0
		
	# Dedicated server?
	
	#debug("server_addr = " + str(server_addr))
	
	if server_addr != None:
		if server_addr == True:
			return dedicated_server()
		else:
			if len(players) > 1:
				sys.stderr.write("Only a single player may be provided when --server is used\n")
				return 1
			if len(players) == 1:
				return client(server_addr, players[0])
			else:
				return client(server_addr)
		
	for i in xrange(len(players)):
		p = make_player(players[i], colour)
		if not isinstance(p, Player):
			sys.stderr.write(sys.argv[0] + " : Fatal error creating " + colour + " player\n")
			return 100
		players[i] = p
		if colour == "white":
			colour = "black"
		elif colour == "black":
			pass
		else:
			sys.stderr.write(sys.argv[0] + " : Too many players (max 2)\n")
		
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
		game = ReplayThread(players, src_file, end=end, max_moves=max_moves)
	else:
		board = Board(style)
		board.max_moves = max_moves
		game = GameThread(board, players) 
		game.retry_illegal = retry_illegal




	# Initialise GUI
	if graphics_enabled == True:
		try:
			graphics = GraphicsThread(game.board, grid_sz = [64,64]) # Construct a GraphicsThread!
			
			graphics.sleep_timeout = sleep_timeout

		except Exception,e:
			graphics = None
			sys.stderr.write(sys.argv[0] + " : Got exception trying to initialise graphics\n"+str(e.message)+"\nDisabled graphics\n")
			graphics_enabled = False

	# If there are no players listed, display a nice pretty menu
	if len(players) != 2:
		if graphics != None:
			
			server_addr = graphics.SelectServer()
			if server_addr != None:
				pygame.quit() # Time to say goodbye
				if server_addr == True:
					return dedicated_server()
				else:
					return client(server_addr)	
			
			players = graphics.SelectPlayers(players)
		else:
			sys.stderr.write(sys.argv[0] + " : Usage " + sys.argv[0] + " white black\n")
			return 44

	# If there are still no players, quit
	if players == None or len(players) != 2:
		sys.stderr.write(sys.argv[0] + " : Graphics window closed before players chosen\n")
		return 45

	old = players[:]
	for p in old:
		if isinstance(p, NetworkPlayer):
			for i in range(len(old)):
				if old[i] == p or isinstance(old[i], NetworkPlayer):
					continue
				players[i] = NetworkPlayer(old[i].colour, p.network, old[i])
		
	for p in players:
		#debug(str(p))
		if isinstance(p, NetworkPlayer):
			p.board = game.board
			if not p.network.connected:
				if not p.network.server:
					time.sleep(0.2)
				p.network.connect()
				
	
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
	

	for l in log_files:
		l.close()

	if src_file != None and src_file != sys.stdin:
		src_file.close()

	sys.stdout.write(game.final_result + "\n")

	return error
		
		
	
		
	
		
		

# This is how python does a main() function...
if __name__ == "__main__":
	retcode = 0
	try:
		retcode = main(sys.argv)
	except KeyboardInterrupt:
		sys.stderr.write(sys.argv[0] + " : Got KeyboardInterrupt. Stopping everything\n")
		if isinstance(graphics, StoppableThread):
			graphics.stop()
			graphics.run() # Will clean up graphics because it is stopped, not run it (a bit dodgy)

		if isinstance(game, StoppableThread):
			game.stop()
			if game.is_alive():
				game.join()
		retcode = 102
	#except Exception, e:
	#	sys.stderr.write(sys.argv[0] + " : " + e.message + "\n")
	#	retcode = 103	
		
	try:
    		sys.stdout.close()
	except:
    		pass
	try:
    		sys.stderr.close()
	except:
    		pass
	sys.exit(retcode)
		

# --- main.py --- #
# EOF - created from make on Monday 24 June  23:55:46 WST 2013
