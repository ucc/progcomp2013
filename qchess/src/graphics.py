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
			
				
			
