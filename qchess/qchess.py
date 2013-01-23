#!/usr/bin/python -u
# +++ board.py +++ #
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
			p.draw(window, grid_sz)

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
			raise Exception("COLOUR")

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
# +++ game.py +++ #

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
					self.state["turn"] = p # "turn" contains the player who's turn it is
				#try:
				if True:
					[x,y] = p.select() # Player selects a square
					if self.stopped():
						break

					result = self.board.select(x, y, colour = p.colour)				
					for p2 in self.players:
						p2.update(result) # Inform players of what happened



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

					result = self.board.update_move(x, y, x2, y2)
					for p2 in self.players:
						p2.update(str(x) + " " + str(y) + " -> " + str(x2) + " " + str(y2)) # Inform players of what happened

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
				#except Exception,e:
					#result = "ILLEGAL " + e.message
					#sys.stderr.write(result + "\n")
					
					#self.stop()
					#with self.lock:
					#	self.final_result = self.state["turn"].colour + " " + "ILLEGAL"

				if self.board.king["black"] == None:
					if self.board.king["white"] == None:
						with self.lock:
							self.final_result = "DRAW"
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

		graphics.stop()

	


def opponent(colour):
	if colour == "white":
		return "black"
	else:
		return "white"
# --- game.py --- #
# +++ graphics.py +++ #
import pygame

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

# A thread to make things pretty
class GraphicsThread(StoppableThread):
	def __init__(self, board, title = "UCC::Progcomp 2013 - QChess", grid_sz = [80,80]):
		StoppableThread.__init__(self)
		
		self.board = board
		pygame.init()
		self.window = pygame.display.set_mode((grid_sz[0] * w, grid_sz[1] * h))
		pygame.display.set_caption(title)
		self.grid_sz = grid_sz[:]
		self.state = {"select" : None, "dest" : None, "moves" : None, "overlay" : None, "coverage" : None}
		self.error = 0
		self.lock = threading.RLock()
		self.cond = threading.Condition()

		# Get the font sizes
		l_size = 5*(self.grid_sz[0] / 8)
		s_size = 3*(self.grid_sz[0] / 8)
		for p in piece_types.keys():
			c = "black"
			images[c].update({p : pygame.font.Font("data/DejaVuSans.ttf", l_size).render(piece_char[c][p], True,(0,0,0))})
			small_images[c].update({p : pygame.font.Font("data/DejaVuSans.ttf", s_size).render(piece_char[c][p],True,(0,0,0))})
			c = "white"

			images[c].update({p : pygame.font.Font("data/DejaVuSans.ttf", l_size+1).render(piece_char["black"][p], True,(255,255,255))})
			images[c][p].blit(pygame.font.Font("data/DejaVuSans.ttf", l_size).render(piece_char[c][p], True,(0,0,0)),(0,0))
			small_images[c].update({p : pygame.font.Font("data/DejaVuSans.ttf", s_size+1).render(piece_char["black"][p],True,(255,255,255))})
			small_images[c][p].blit(pygame.font.Font("data/DejaVuSans.ttf", s_size).render(piece_char[c][p],True,(0,0,0)),(0,0))

		
	


	# On the run from the world
	def run(self):
		
		while not self.stopped():
			
			self.board.display_grid(window = self.window, grid_sz = self.grid_sz) # Draw the board

			self.overlay()

			self.board.display_pieces(window = self.window, grid_sz = self.grid_sz) # Draw the board		

			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					if isinstance(game, GameThread):
						with game.lock:
							game.final_result = "terminated"
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
						font = pygame.font.Font(None, 14)
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
				font = pygame.font.Font(None, 14)
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
	def message(self, string, pos = None, colour = None, font_size = 32):
		font = pygame.font.Font(None, font_size)
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
		result = ""
		while True:
			#print "LOOP"
			if prompt != None:
				self.message(prompt)
				self.message(result, pos = (0, 1))
	
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					if chr(event.key) == '\r':
						return result
					result += str(chr(event.key))
# --- graphics.py --- #
# +++ main.py +++ #
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


# The main function! It does the main stuff!
def main(argv):

	# Apparently python will silently treat things as local unless you do this
	# But (here's the fun part), only if you actually modify the variable.
	# For example, all those 'if graphics_enabled' conditions work in functions that never say it is global
	# Anyone who says "You should never use a global variable" can die in a fire
	global game
	global graphics

	# Magical argument parsing goes here
	if len(argv) == 1:
		players = [HumanPlayer("saruman", "white"), AgentRandom("sabbath", "black")]
	elif len(argv) == 2:
		players = [AgentPlayer(argv[1], "white"), HumanPlayer("shadow", "black"), ]
	elif len(argv) == 3:
		players = [AgentPlayer(argv[1], "white"), AgentPlayer(argv[2], "black")]

	# Construct the board!
	board = Board(style = "quantum")
	game = GameThread(board, players) # Construct a GameThread! Make it global! Damn the consequences!
	#try:
	if True:
		graphics = GraphicsThread(board, grid_sz = [64,64]) # Construct a GraphicsThread! I KNOW WHAT I'M DOING! BEAR WITH ME!
		game.start() # This runs in a new thread
	#except NameError:
	#	print "Run game in main thread"
	#	game.run() # Run game in the main thread (no need for joining)
	#	return game.error
	#except Exception, e:
	#	raise e
	#else:
	#	print "Normal"
		graphics.run()
		game.join()
		return game.error + graphics.error


# This is how python does a main() function...
if __name__ == "__main__":
	sys.exit(main(sys.argv))
# --- main.py --- #
# +++ piece.py +++ #
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
		return str(self.current_type) + " " + str(self.types) + " at " + str(self.x) + ","+str(self.y)  

	# Draw the piece in a pygame surface
	def draw(self, window, grid_sz = [80,80]):

		# First draw the image corresponding to self.current_type
		img = images[self.colour][self.current_type]
		rect = img.get_rect()
		offset = [-rect.width/2,-3*rect.height/4] 
		window.blit(img, (self.x * grid_sz[0] + grid_sz[0]/2 + offset[0], self.y * grid_sz[1] + grid_sz[1]/2 + offset[1]))
		
		
		# Draw the two possible types underneath the current_type image
		for i in range(len(self.types)):
			if self.types_revealed[i] == True:
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
# +++ player.py +++ #
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
# --- player.py --- #
# +++ thread_util.py +++ #
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
