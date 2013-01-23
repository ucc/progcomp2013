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
