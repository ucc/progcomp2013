def dedicated_server():
	max_games = 4
	games = []
	while True:
		# Get players
		s = socket.socket()
		s.bind(("0.0.0.0", 4562))
		s.listen(2)
		ss = s.accept()
		
		debug("Got white player")
		
		g = subprocess.Popen(["python", "qchess.py", "@network::"+str(4700+len(games)), "@network::"+str(4700+len(games)), "--log="+"_".join(str(datetime.datetime.now()).split(" ")) + ".log"], stdout=subprocess.PIPE)
		games.append(g)
		
		ss[0].send("white " + str(4700 + len(games)-1))
		ss[0].shutdown(socket.SHUT_RDWR)
		ss[0].close()
		
		time.sleep(0.5)
		ss = s.accept()
		
		debug("Got black player")
		
		ss[0].send("black " + str(4700 + len(games)-1))
		ss[0].shutdown(socket.SHUT_RDWR)
		ss[0].close()
		
		s.shutdown(socket.SHUT_RDWR)
		s.close()
		
		while len(games) > max_games:
			ready = select.select(map(lambda e : e.stdout, games),[], [], None)
			for r in ready:
				s = r.readline().strip(" \r\n").split(" ")
				if s[0] == "white" or s[0] == "black":
					for g in games[:]:
						if g.stdout == r:
							games.remove(g)
	
def client(addr):
	
	s = socket.socket()
	s.connect((addr, 4562))
	
	[colour,port] = s.recv(1024).strip(" \r\n").split(" ")
	
	debug("Colour: " + colour + ", port: " + port)
	
	s.shutdown(socket.SHUT_RDWR)
	s.close()
	
	if colour == "white":
		p = subprocess.Popen(["python", "qchess.py", "@human", "@network:"+addr+":"+port])
	else:
		p = subprocess.Popen(["python", "qchess.py", "@network:"+addr+":"+port, "@human"])
	p.wait()
	sys.exit(0)