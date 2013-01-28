
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

		graphics.stop()

	


def opponent(colour):
	if colour == "white":
		return "black"
	else:
		return "white"
