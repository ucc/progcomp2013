#!/usr/bin/python -u

from qchess import *

"""
	Agent Bishop
	( an agent, not an implementation of a bishop chess piece!)
"""




# Skeleton class for your agent
class Agent(AgentRandom): # Inherits from AgentRandom (in qchess.py)
	def __init__(self, name, colour):
		AgentRandom.__init__(self, name, colour)
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

		#sys.stderr.write(sys.argv[0] + ": prioritise called for " + str(piece) + "\n")

		
		
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
		
		self.choice = self.select_best(self.colour)[0]
		return [self.choice.x, self.choice.y]
	
	# Returns [x,y] of square to move selected piece into
	def get_move(self):
		self.choice.selected_moves = self.choice.last_moves
		moves = self.prioritise_moves(self.choice)
		if len(moves) > 0:
			return moves[0][0]
		else:
			return AgentRandom.get_move(self)

		
		
		
# Horrible messy graphics class that draws what the agent is doing, kind of useful for testing
class AgentGraphics(GraphicsThread):
	def __init__(self, board, title):
		GraphicsThread.__init__(self, board, title, grid_sz = [64,64])
		self.choice = None
		self.moves = None

	def run(self):
		square_img = pygame.Surface((self.grid_sz[0], self.grid_sz[1]),pygame.SRCALPHA) # A square image
		while not self.stopped():
		
			self.board.display_grid(window = self.window, grid_sz = self.grid_sz)	

			# Draw choice of the AI
			if agent.choice != None:
				mp = [self.grid_sz[i] * [agent.choice.x, agent.choice.y][i] for i in range(2)]
				square_img.fill(pygame.Color(0,255,0,64))
				self.window.blit(square_img, mp)

			# Draw calculated choices for the piece clicked on
			if self.choice != None:
				mp = [self.grid_sz[i] * [self.choice.x, self.choice.y][i] for i in range(2)]
				square_img.fill(pygame.Color(0,0,255,128))
				self.window.blit(square_img, mp)

			# Draw the choices the AI calculated from the selection of the chosen piece
			if agent.choice != None and agent.choice.selected_moves != None:
				for m in agent.choice.selected_moves:
					mp = [m[0][i] * self.grid_sz[i] for i in range(2)]
					square_img.fill(pygame.Color(128,128,255,128))
					self.window.blit(square_img, mp)
					font = pygame.font.Font(None, 14)
					text = font.render("{0:.2f}".format(round(m[1],2)), 1, pygame.Color(255,0,0))
					mp[0] = mp[0] + self.grid_sz[0] - text.get_width()
					mp[1] = mp[1] + self.grid_sz[1] - text.get_height()
					self.window.blit(text, mp)


			# Draw the choice the AI's chosen piece could have actually made
			if agent.choice != None and agent.choice.last_moves != None:
				for m in agent.choice.last_moves:
					mp = [m[0][i] * self.grid_sz[i] for i in range(2)]
					square_img.fill(pygame.Color(255,0,0,128))
					self.window.blit(square_img, mp)
					font = pygame.font.Font(None, 14)
					text = font.render("{0:.2f}".format(round(m[1],2)), 1, pygame.Color(0,0,255))
					mp[0] = mp[0] + self.grid_sz[0] - text.get_width()
					self.window.blit(text, mp)

			


			if self.moves != None:
				for m in self.moves:
					mp = [m[0][i] * self.grid_sz[i] for i in range(2)]
					square_img.fill(pygame.Color(255,0,255,128))
					self.window.blit(square_img, mp)
					font = pygame.font.Font(None, 14)
					text = font.render("{0:.2f}".format(round(m[1],2)), 1, pygame.Color(0,0,0))
					self.window.blit(text, mp)
			
			
	
			self.board.display_pieces(window = self.window, grid_sz = self.grid_sz)

			pygame.display.flip()
			
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.stop()
					break
				elif event.type == pygame.MOUSEBUTTONDOWN:
					m = [event.pos[i] / self.grid_sz[i] for i in range(len(event.pos))]
					p = agent.board.grid[m[0]][m[1]]
					if p == None:
						continue
					self.choice = p
					self.last_moves = self.choice.last_moves
					self.selected_moves = self.choice.selected_moves
					if event.button == 3 or self.choice.last_moves == None:
						self.moves = agent.prioritise_moves(self.choice)
					else:
						self.moves = self.choice.last_moves
					
				elif event.type == pygame.MOUSEBUTTONUP:
					if self.choice == None:
						continue
					self.choice.last_moves = self.last_moves
					self.choice.selected_moves = self.selected_moves
					self.choice = None
					self.moves = None
					
		pygame.display.quit()				
		


# Main function; don't alter
def main(argv):

	global agent
	colour = sys.stdin.readline().strip("\n") # Gets the colour of the agent from stdin
	
	agent = Agent(argv[0], colour) # Creates your agent

	graphics = AgentGraphics(agent.board, title="Agent Bishop (" + str(colour) + ") - DEBUG VIEW")
	graphics.start()

	# Plays quantum chess using your agent
	while True:
		line = sys.stdin.readline().strip(" \r\n")
		#sys.stderr.write(argv[0] + ": gets line \"" + str(line) + "\"\n")
		if line == "SELECTION?":
			[x,y] = agent.select() # Gets your agent's selection
			#print "Select " + str(x) + "," + str(y)
			sys.stdout.write(str(x) + " " + str(y) + "\n")				
		elif line == "MOVE?":
			[x,y] = agent.get_move() # Gets your agent's move
			sys.stdout.write(str(x) + " " + str(y) + "\n")
		elif line.split(" ")[0] == "QUIT":
			agent.quit(" ".join(line.split(" ")[1:])) # Quits the game
#			graphics.stop()
			break
		else:
			agent.update(line) # Updates agent.board

	graphics.stop()
	graphics.join()
	return 0

# Don't touch this
if __name__ == "__main__":
	sys.exit(main(sys.argv))
