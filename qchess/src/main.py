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
		if s[0] == "internal":

			import inspect
			internal_agents = inspect.getmembers(sys.modules[__name__], inspect.isclass)
			internal_agents = [x for x in internal_agents if issubclass(x[1], InternalAgent)]
			internal_agents.remove(('InternalAgent', InternalAgent)) 
			
			if len(s) != 2:
				sys.stderr.write(sys.argv[0] + " : '@internal' should be followed by ':' and an agent name\n")
				sys.stderr.write(sys.argv[0] + " : Choices are: " + str(map(lambda e : e[0], internal_agents)) + "\n")
				return None

			for a in internal_agents:
				if s[1] == a[0]:
					return a[1](name, colour)
			
			sys.stderr.write(sys.argv[0] + " : Can't find an internal agent matching \"" + s[1] + "\"\n")
			sys.stderr.write(sys.argv[0] + " : Choices are: " + str(map(lambda e : e[0], internal_agents)) + "\n")
			return None
			

	else:
		return ExternalAgent(name, colour)
			


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
	global graphics_enabled


	src_file = None
	
	style = "quantum"
	colour = "white"

	# Get the important warnings out of the way
	if platform.system() == "Windows":
		sys.stderr.write(sys.argv[0] + " : Warning - You are using " + platform.system() + "\n")
		if platform.release() == "Vista":
			sys.stderr.write(sys.argv[0] + " : God help you.\n")
	

	players = []
	i = 0
	while i < len(argv)-1:
		i += 1
		arg = argv[i]
		if arg[0] != '-':
			p = make_player(arg, colour)
			if not isinstance(p, Player):
				sys.stderr.write(sys.argv[0] + " : Fatal error creating " + colour + " player\n")
				return 100
			players.append(p)
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
				src_file = sys.stdin
			else:
				src_file = open(arg[2:].split("=")[1])
		elif (arg[1] == '-' and arg[2:].split("=")[0] == "log"):
			# Log file
			if len(arg[2:].split("=")) == 1:
				log_file = sys.stdout
			else:
				log_file = open(arg[2:].split("=")[1], "w")
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
			else:
				agent_timeout = float(arg[2:].split("=")[1])
				
		elif (arg[1] == '-' and arg[2:] == "help"):
			# Help
			os.system("less data/help.txt") # The best help function
			return 0


	# Create the board
	
	# Construct a GameThread! Make it global! Damn the consequences!
			
	if src_file != None:
		if len(players) == 0:
			players = [Player("dummy", "white"), Player("dummy", "black")]
		game = ReplayThread(players, src_file)
	else:
		board = Board(style)
		game = GameThread(board, players) 



	# Initialise GUI
	if graphics_enabled == True:
		try:
			graphics = GraphicsThread(game.board, grid_sz = [64,64]) # Construct a GraphicsThread!

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

	
	# If using windows, select won't work; use horrible TimeoutPlayer hack
	if agent_timeout > 0:
		if platform.system() == "Windows":
			for i in range(len(players)):
				if isinstance(players[i], ExternalAgent) or isinstance(players[i], InternalAgent):
					players[i] = TimeoutPlayer(players[i], agent_timeout)

		else:
			warned = False
			# InternalAgents get wrapped to an ExternalAgent when there is a timeout
			# This is not confusing at all.
			for i in range(len(players)):
				if isinstance(players[i], InternalAgent):
						players[i] = ExternalWrapper(players[i])


		




	
	if graphics != None:
		game.start() # This runs in a new thread
		graphics.run()
		game.join()
		error = game.error + graphics.error
	else:
		game.run()
		error = game.error

	if log_file != None and log_file != sys.stdout:
		log_file.close()

	if src_file != None and src_file != sys.stdin:
		src_file.close()

	return error

# This is how python does a main() function...
if __name__ == "__main__":
	sys.exit(main(sys.argv))
