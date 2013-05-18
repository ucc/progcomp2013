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

