


	

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
