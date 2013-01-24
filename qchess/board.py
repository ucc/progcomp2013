[w,h] = [8,8] # Width and height of board(s)

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
