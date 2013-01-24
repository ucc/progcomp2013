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

def make_player(name, colour):
	if name[0] == '@':
		if name[1:] == "human":
			return HumanPlayer(name, colour)
		s = name[1:].split(":")
		if s[0] == "network":
			address = None
			if len(s) > 1:
				address = s[1]
			return NetworkReceiver(colour, address)

	else:
		return AgentPlayer(name, colour)
			


# The main function! It does the main stuff!
def main(argv):

	# Apparently python will silently treat things as local unless you do this
	# Anyone who says "You should never use a global variable" can die in a fire
	global game
	global graphics
	
	global turn_delay
	global agent_timeout
	global log_file
	global src_file



	
	style = "quantum"
	colour = "white"
	graphics_enabled = True

	players = []
	i = 0
	while i < len(argv)-1:
		i += 1
		arg = argv[i]
		if arg[0] != '-':
			players.append(make_player(arg, colour))
			if colour == "white":
				colour = "black"
			elif colour == "black":
				pass
			else:
				sys.stderr.write(sys.argv[0] + " : Too many players (max 2)\n")
			continue

		# Option parsing goes here
		if arg[1] == '-' and arg[2:] == "classical":
			style = "classical"
		elif arg[1] == '-' and arg[2:] == "quantum":
			style = "quantum"
		elif (arg[1] == '-' and arg[2:] == "graphics"):
			graphics_enabled = not graphics_enabled
		elif (arg[1] == '-' and arg[2:].split("=")[0] == "file"):
			# Load game from file
			if len(arg[2:].split("=")) == 1:
				src_file = sys.stdout
			else:
				src_file = arg[2:].split("=")[1]
		elif (arg[1] == '-' and arg[2:].split("=")[0] == "log"):
			# Log file
			if len(arg[2:].split("=")) == 1:
				log_file = sys.stdout
			else:
				log_file = arg[2:].split("=")[1]
		elif (arg[1] == '-' and arg[2:].split("=")[0] == "delay"):
			# Delay
			if len(arg[2:].split("=")) == 1:
				turn_delay = 0
			else:
				turn_delay = float(arg[2:].split("=")[1])

		elif (arg[1] == '-' and arg[2:].split("=")[0] == "timeout"):
			# Timeout
			if len(arg[2:].split("=")) == 1:
				agent_timeout = -1
			elif platform.system() != "Windows": # Windows breaks this option
				agent_timeout = float(arg[2:].split("=")[1])
			else:
				sys.stderr.write(sys.argv[0] + " : Warning - You are using Windows\n")
				agent_timeout = -1
				
		elif (arg[1] == '-' and arg[2:] == "help"):
			# Help
			os.system("less data/help.txt") # The best help function
			return 0


	# Create the board
	board = Board(style)


	# Initialise GUI
	if graphics_enabled == True:
		try:
			graphics = GraphicsThread(board, grid_sz = [64,64]) # Construct a GraphicsThread!
		except Exception,e:
			graphics = None
			sys.stderr.write(sys.argv[0] + " : Got exception trying to initialise graphics\n"+str(e.message)+"\nDisabled graphics\n")
			graphics_enabled = False

	# If there are no players listed, display a nice pretty menu
	if len(players) != 2:
		if graphics != None:
			players = graphics.SelectPlayers(players)
		else:
			sys.stderr.write(sys.argv[0] + " : Usage " + sys.argv[0] + " white black\n")
			return 44

	# If there are still no players, quit
	if players == None or len(players) != 2:
		sys.stderr.write(sys.argv[0] + " : Graphics window closed before players chosen\n")
		return 45


	# Wrap NetworkSender players around original players if necessary
	for i in range(len(players)):
		if isinstance(players[i], NetworkReceiver):
			players[i].board = board # Network players need direct access to the board
			for j in range(len(players)):
				if j == i:
					continue
				if isinstance(players[j], NetworkSender) or isinstance(players[j], NetworkReceiver):
					continue
				players[j] = NetworkSender(players[j], players[i].address)
				players[j].board = board

	# Connect the networked players
	for p in players:
		if isinstance(p, NetworkSender) or isinstance(p, NetworkReceiver):
			if graphics != None:
				graphics.board.display_grid(graphics.window, graphics.grid_sz)
				graphics.message("Connecting to " + p.colour + " player...")
			p.connect()


	# Construct a GameThread! Make it global! Damn the consequences!
	game = GameThread(board, players) 


	
	if graphics != None:
		game.start() # This runs in a new thread
		graphics.run()
		game.join()
		return game.error + graphics.error
	else:
		game.run()
		return game.error

# This is how python does a main() function...
if __name__ == "__main__":
	sys.exit(main(sys.argv))
