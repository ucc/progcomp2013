


	

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
					if isinstance(p, Network) and p.baseplayer != None:
						self.state["turn"] = p.baseplayer # "turn" contains the player who's turn it is
					else:
						self.state["turn"] = p
				#try:
				if True:
					[x,y] = p.select() # Player selects a square
					if self.stopped():
						break
						
					if isinstance(p, Network) == False or p.server == True:
						result = self.board.select(x, y, colour = p.colour)
					else:
						result = p.get_response()
						self.board.update(result)
						
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
