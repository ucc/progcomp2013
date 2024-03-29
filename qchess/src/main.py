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
sleep_timeout = None
[game, graphics] = [None, None]

def make_player(name, colour):
	debug(name)
	if name[0] == '@':
		if name[1:] == "human":
			return HumanPlayer(name, colour)
		s = name[1:].split(":")
		if s[0] == "network":
			ip = None
			port = 4562
			#print str(s)
			if len(s) > 1:
				if s[1] != "":
					ip = s[1]
			if len(s) > 2:
				port = int(s[2])
				
			if ip == None:
				if colour == "black":
					port += 1
			elif colour == "white":
				port += 1
						
			return NetworkPlayer(colour, Network((ip, port)), None)
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
		if s[0] == "fifo":
			if len(s) > 1:
				return FifoPlayer(s[1], colour)
			else:
				return FifoPlayer(str(os.getpid())+"."+colour, colour)

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
	global log_files
	global src_file
	global graphics_enabled
	global always_reveal_states
	global sleep_timeout


	retry_illegal = False
	server_addr = None

	max_moves = None
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
			players.append(arg)
			continue

		# Option parsing goes here
		if arg[1] == '-' and arg[2:] == "classical":
			style = "classical"
		elif arg[1] == '-' and arg[2:] == "quantum":
			style = "quantum"
		elif arg[1] == '-' and arg[2:] == "reveal":
			always_reveal_states = True
		elif (arg[1] == '-' and arg[2:] == "graphics"):
			graphics_enabled = True
		elif (arg[1] == '-' and arg[2:] == "no-graphics"):
			graphics_enabled = False
		elif (arg[1] == '-' and arg[2:].split("=")[0] == "file"):
			# Load game from file
			if len(arg[2:].split("=")) == 1:
				src_file = sys.stdin
			else:
				f = arg[2:].split("=")[1]
				if f[0:7] == "http://":
					src_file = HttpReplay(f)
				else:
					src_file = FileReplay(f.split(":")[0])

					if len(f.split(":")) == 2:
						max_moves = int(f.split(":")[1])
						
		elif (arg[1] == '-' and arg[2:].split("=")[0] == "server"):
			#debug("Server: " + str(arg[2:]))
			if len(arg[2:].split("=")) <= 1:
				server_addr = True
			else:
				server_addr = arg[2:].split("=")[1]
			
		elif (arg[1] == '-' and arg[2:].split("=")[0] == "log"):
			# Log file
			if len(arg[2:].split("=")) == 1:
				log_files.append(LogFile(sys.stdout,""))
			else:
				f = arg[2:].split("=")[1]
				if f == "":
					log_files.append(LogFile(sys.stdout, ""))
				elif f[0] == '@':
					log_files.append(ShortLog(f[1:]))
				else:
					log_files.append(LogFile(open(f, "w", 0), f))
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
		elif (arg[1] == '-' and arg[2:].split("=")[0] == "blackout"):
			# Screen saver delay
			if len(arg[2:].split("=")) == 1:
				sleep_timeout = -1
			else:
				sleep_timeout = float(arg[2:].split("=")[1])
		elif (arg[1] == '-' and arg[2:] == "retry-illegal"):
			retry_illegal = not retry_illegal
		elif (arg[1] == '-' and arg[2:] == "help"):
			# Help
			os.system("less data/help.txt") # The best help function
			return 0
		
	# Dedicated server?
	
	#debug("server_addr = " + str(server_addr))
	
	if server_addr != None:
		if server_addr == True:
			return dedicated_server()
		else:
			if len(players) > 1:
				sys.stderr.write("Only a single player may be provided when --server is used\n")
				return 1
			if len(players) == 1:
				return client(server_addr, players[0])
			else:
				return client(server_addr)
		
	for i in xrange(len(players)):
		p = make_player(players[i], colour)
		if not isinstance(p, Player):
			sys.stderr.write(sys.argv[0] + " : Fatal error creating " + colour + " player\n")
			return 100
		players[i] = p
		if colour == "white":
			colour = "black"
		elif colour == "black":
			pass
		else:
			sys.stderr.write(sys.argv[0] + " : Too many players (max 2)\n")
		
	# Create the board
	
	# Construct a GameThread! Make it global! Damn the consequences!
			
	if src_file != None:
		# Hack to stop ReplayThread from exiting
		#if len(players) == 0:
		#	players = [HumanPlayer("dummy", "white"), HumanPlayer("dummy", "black")]

		# Normally the ReplayThread exits if there are no players
		# TODO: Decide which behaviour to use, and fix it
		end = (len(players) == 0)
		if end:
			players = [Player("dummy", "white"), Player("dummy", "black")]
		elif len(players) != 2:
			sys.stderr.write(sys.argv[0] + " : Usage " + sys.argv[0] + " white black\n")
			if graphics_enabled:
				sys.stderr.write(sys.argv[0] + " : (You won't get a GUI, because --file was used, and the author is lazy)\n")
			return 44
		game = ReplayThread(players, src_file, end=end, max_moves=max_moves)
	else:
		board = Board(style)
		board.max_moves = max_moves
		game = GameThread(board, players) 
		game.retry_illegal = retry_illegal




	# Initialise GUI
	if graphics_enabled == True:
		try:
			graphics = GraphicsThread(game.board, grid_sz = [64,64]) # Construct a GraphicsThread!
			
			graphics.sleep_timeout = sleep_timeout

		except Exception,e:
			graphics = None
			sys.stderr.write(sys.argv[0] + " : Got exception trying to initialise graphics\n"+str(e.message)+"\nDisabled graphics\n")
			graphics_enabled = False

	# If there are no players listed, display a nice pretty menu
	if len(players) != 2:
		if graphics != None:
			
			server_addr = graphics.SelectServer()
			if server_addr != None:
				pygame.quit() # Time to say goodbye
				if server_addr == True:
					return dedicated_server()
				else:
					return client(server_addr)	
			
			players = graphics.SelectPlayers(players)
		else:
			sys.stderr.write(sys.argv[0] + " : Usage " + sys.argv[0] + " white black\n")
			return 44

	# If there are still no players, quit
	if players == None or len(players) != 2:
		sys.stderr.write(sys.argv[0] + " : Graphics window closed before players chosen\n")
		return 45

	old = players[:]
	for p in old:
		if isinstance(p, NetworkPlayer):
			for i in range(len(old)):
				if old[i] == p or isinstance(old[i], NetworkPlayer):
					continue
				players[i] = NetworkPlayer(old[i].colour, p.network, old[i])
		
	for p in players:
		#debug(str(p))
		if isinstance(p, NetworkPlayer):
			p.board = game.board
			if not p.network.connected:
				if not p.network.server:
					time.sleep(0.2)
				p.network.connect()
				
	
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


		




	log_init(game.board, players)
	
	
	if graphics != None:
		game.start() # This runs in a new thread
		graphics.run()
		if game.is_alive():
			game.join()
	

		error = game.error + graphics.error
	else:
		game.run()
		error = game.error
	

	for l in log_files:
		l.close()

	if src_file != None and src_file != sys.stdin:
		src_file.close()

	sys.stdout.write(game.final_result + "\n")

	return error
		
		
	
		
	
		
		

# This is how python does a main() function...
if __name__ == "__main__":
	retcode = 0
	try:
		retcode = main(sys.argv)
	except KeyboardInterrupt:
		sys.stderr.write(sys.argv[0] + " : Got KeyboardInterrupt. Stopping everything\n")
		if isinstance(graphics, StoppableThread):
			graphics.stop()
			graphics.run() # Will clean up graphics because it is stopped, not run it (a bit dodgy)

		if isinstance(game, StoppableThread):
			game.stop()
			if game.is_alive():
				game.join()
		retcode = 102
	#except Exception, e:
	#	sys.stderr.write(sys.argv[0] + " : " + e.message + "\n")
	#	retcode = 103	
		
	try:
    		sys.stdout.close()
	except:
    		pass
	try:
    		sys.stderr.close()
	except:
    		pass
	sys.exit(retcode)
		

