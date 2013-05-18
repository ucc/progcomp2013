import multiprocessing

# Hacky alternative to using select for timing out players

# WARNING: Do not wrap around HumanPlayer or things breakify
# WARNING: Do not use in general or things breakify

class Sleeper(multiprocessing.Process):
	def __init__(self, timeout):
		multiprocessing.Process.__init__(self)
		self.timeout = timeout

	def run(self):
		time.sleep(self.timeout)


class Worker(multiprocessing.Process):
	def __init__(self, function, args, q):
		multiprocessing.Process.__init__(self)
		self.function = function
		self.args = args
		self.q = q

	def run(self):
		#print str(self) + " runs " + str(self.function) + " with args " + str(self.args)
		#try:
		self.q.put(self.function(*self.args))
		#except IOError:
		#	pass
		
		

def TimeoutFunction(function, args, timeout):
	q = multiprocessing.Queue()
	w = Worker(function, args, q)
	s = Sleeper(timeout)
	w.start()
	s.start()
	while True: # Busy loop of crappyness
		if not w.is_alive():
			s.terminate()
			result = q.get()
			w.join()
			#print "TimeoutFunction gets " + str(result)
			return result
		elif not s.is_alive():
			w.terminate()
			s.join()
			raise Exception("TIMEOUT")
		time.sleep(0.1)
	
		

# A player that wraps another player and times out its moves
# Uses threads
# A (crappy) alternative to the use of select()
class TimeoutPlayer(Player):
	def __init__(self, base_player, timeout):
		Player.__init__(self, base_player.name, base_player.colour)
		self.base_player = base_player
		self.timeout = timeout
		
	def select(self):
		return TimeoutFunction(self.base_player.select, [], self.timeout)
		
	
	def get_move(self):
		return TimeoutFunction(self.base_player.get_move, [], self.timeout)

	def update(self, result):
		return TimeoutFunction(self.base_player.update, [result], self.timeout)

	def quit(self, final_result):
		return TimeoutFunction(self.base_player.quit, [final_result], self.timeout)
