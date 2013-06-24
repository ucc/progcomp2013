def dedicated_server():
	global log_files
	
	max_games = 5
	games = []
	gameID = 0
	while True:
		# Get players
		gameID += 1
		log("Getting clients...")
		s = socket.socket()
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(("0.0.0.0", 4562))
		s.listen(2)
		ss = s.accept()
		
		log("Got white player")
		
		args = ["python", "qchess.py", "--no-graphics", "@network::"+str(4600+2*len(games)), "@network::"+str(4600+2*len(games))]
		if len(log_files) != 0:
			for l in log_files:
				if l.name == "":
					args.append("--log")
				else:
					args.append("--log="+str(l.name)+"_"+str(gameID))
		
		g = subprocess.Popen(args, stdout=subprocess.PIPE)
		games.append(g)
		
		time.sleep(0.5)
		ss[0].send("white " + str(4600 + 2*(len(games)-1)))
		ss[0].shutdown(socket.SHUT_RD)
		ss[0].close()
		
		time.sleep(0.5)
		ss = s.accept()
		
		log("Got black player")
		
		time.sleep(0.5)
		ss[0].send("black " + str(4600 + 2*(len(games)-1)))
		ss[0].shutdown(socket.SHUT_RD)
		ss[0].close()
		
		s.shutdown(socket.SHUT_RDWR)
		s.close()
		
		
		while len(games) > max_games:
			#log("Too many games; waiting for game to finish...")
			ready = select.select(map(lambda e : e.stdout, games),[], [])
			for r in ready[0]:
				s = r.readline().strip(" \r\n").split(" ")
				if s[0] == "white" or s[0] == "black":
					for g in games[:]:
						if g.stdout == r:
							log("Game " + str(g) + " has finished")
							games.remove(g)
							
	return 0
	
def client(addr, player="@human"):
	
	
	debug("Client " + player + " starts")
	s = socket.socket()
	s.connect((addr, 4562))
	
	[colour,port] = s.recv(1024).strip(" \r\n").split(" ")
	
	debug("Colour: " + colour + ", port: " + port)
	
	s.shutdown(socket.SHUT_RDWR)
	s.close()
	
	if colour == "white":
		p = subprocess.Popen(["python", "qchess.py", player, "@network:"+addr+":"+port])
	else:
		p = subprocess.Popen(["python", "qchess.py", "@network:"+addr+":"+port, player])
	p.wait()
	return 0
