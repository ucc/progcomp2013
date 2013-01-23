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
