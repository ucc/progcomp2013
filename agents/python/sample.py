#!/usr/bin/python -u

# Sample agent
# Copy this file, change the agent as needed

from qchess import * # This is normally considered bad practice in python, but good practice in UCC::Progcomp
import random # For the example which makes random moves

debug = False

# The first thing to do is pick a cool name...
class AgentSample(InternalAgent): 
	def __init__(self, name, colour):
		InternalAgent.__init__(self, name, colour) # The InternalAgent class gives you some useful stuff

		# You can access self.board to get a qchess.Board that stores the state as recorded by the agent
		# This board is automatically updated by the InternalAgent base class
		# As well as a grid of pieces, qchess.Board gives you lists of pieces and other useful functions; see qchess/src/board.py
		

		#TODO: Any extra initialisation
		
		# You should print debug messages like this:
		if debug:
			sys.stderr.write(sys.argv[0] + " : Initialised agent\n")
		

	# Must return [x,y] of selected piece
	# Your agent will call select(), followed by get_move() and so on
	# TODO: Implement
	def select(self):
		# debug message
		if debug:
			sys.stderr.write(sys.argv[0] + " : Selecting piece...\n")
		

		# Here is a random choice algorithm to help you start
		# It is a slight improvement on purely random; it will pick a piece that has at least one known possible move
		# BUT it has a possibility to loop infinitely! You should fix that.

		while True:
			# Randomly pick a piece
			# Use self.board.pieces[self.colour] to get a list of your pieces
			# Use self.board.pieces[opponent(self.colour)] to get opponent pieces
			# Use self.board.king[self.colour], vice versa, to get the king

			choices = self.board.pieces[self.colour] # All the agent's pieces
			choice_index = random.randint(0, len(choices)-1) # Get the index in the list of the chosen piece
			self.choice = choices[choice_index] # Choose the piece, and remember it
			
			# Find all known possible moves for the piece
			# Use self.board.possible_moves(piece) to get a list of possible moves for a piece
			# *BUT* Make sure the type of the piece is known (you can temporarily set it) first!
			# Use Piece.current_type to get/set the current type of a piece

			all_moves = [] # Will store all possible moves for the piece
			tmp = self.choice.current_type # Remember the chosen piece's current type

			if tmp == "unknown": # For pieces that are in a supperposition, try both types
				for t in self.choice.types:
					if t == "unknown":
						continue # Ignore unknown types
					self.choice.current_type = t # Temporarily overwrite the piece's type
					all_moves += self.board.possible_moves(self.choice) # Add the possible moves for that type
			else:
				all_moves = self.board.possible_moves(self.choice) # The piece is in a classical state; add possible moves
			self.choice.current_type = tmp # Reset the piece's current type
			if len(all_moves) > 0:
				break # If the piece had *any* possible moves, it is a good choice; leave the loop
			# Otherwise the loop will try again
		# End while loop
	
		return [self.choice.x, self.choice.y] # Return the position of the selected piece

	# Must return [x,y] of square to move the piece previously selected into
	# Your agent will call select(), followed by get_move() and so on
	# TODO: Implement this
	def get_move(self):	
		# debug message
		if debug:
			sys.stderr.write(sys.argv[0] + " : Moving piece ("+str(self.choice)+")\n")
		# As an example we will just pick a random move for the piece previously chosen in select()

		# Note that whichever piece was previously selected will have collapsed into a classical state

		# self.board.possible_moves(piece) will return a list of [x,y] pairs for valid moves

		moves = self.board.possible_moves(self.choice) # Get all moves for the selected piece
		move_index = random.randint(0, len(moves)-1) # Get the index in the list of the chosen move
		return moves[move_index] # This is a randomly chosen [x,y] pair for a valid move of the piece


# Hints:
# select will probably have to be more complicated than get_move, because by the time get_move is called, the piece's state is known
# If you want to see if a square is threatened/defended, you can call self.board.coverage([x,y]); see qchess/src/board.py
# A good approach is min/max. For each move, associate a score. Then subtract the scores for moves that the opponent could make. Then pick the move with the highest score.
# Look at qchess/src/agent_bishop.py for a more effective (but less explained) agent

if __name__ == "__main__":

	# Parse arguments here
	for i in range(len(sys.argv)):
		if sys.argv[i] == "--debug":
			debug = True
		elif sys.argv[i] == "--no-debug":
			debug = False

	colour = sys.stdin.readline().strip("\r\n")
	agent = AgentSample(sys.argv[0], colour) # Change the class name here
	run_agent(agent) # This is provided by qchess. It calls the functions of your agent as required during the game.

# You can run this as an external agent with the qchess program
# Just run ./qchess.py and apply common sense (or read the help file)

# If you are feeling adventurous you can add it to the qchess program as an internal agent
# This might give better performance... unless you use the --timeout switch, in which case there is absolutely no point
# 1. Delete the lines that run the agent (the block that starts with if __name__ == "__main__")
# 2. Copy the file to qchess/src/agent_sample.py (or whatever you want to call it)
# 3. Edit qchess/src/Makefile so that agent_sample.py appears as one of the files in COMPONENTS
# 4. Rebuild by running make in qchess
# Again, run ./qchess.py and apply common sense

	

