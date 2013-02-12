log_files = []
import datetime
import urllib2

class LogFile():
	def __init__(self, log):	
		
		self.log = log
		self.logged = []
		self.log.write("# Log starts " + str(datetime.datetime.now()) + "\n")

	def write(self, s):
		now = datetime.datetime.now()
		self.log.write(str(now) + " : " + s + "\n")
		self.logged.append((now, s))

	def setup(self, board, players):
		
		for p in players:
			self.log.write("# " + p.colour + " : " + p.name + "\n")
		
		self.log.write("# Initial board\n")
		for x in range(0, w):
			for y in range(0, h):
				if board.grid[x][y] != None:
					self.log.write(str(board.grid[x][y]) + "\n")

		self.log.write("# Start game\n")

	def close(self):
		self.log.write("# EOF\n")
		if self.log != sys.stdout:
			self.log.close()

class ShortLog(LogFile):
	def __init__(self, file_name):
		if file_name == "":
			self.log = sys.stdout
		else:
			self.log = open(file_name, "w", 0)
		LogFile.__init__(self, self.log)
		self.file_name = file_name
		self.phase = 0

	def write(self, s):
		now = datetime.datetime.now()
		self.logged.append((now, s))
		
		if self.phase == 0:
			if self.log != sys.stdout:
				self.log.close()
				self.log = open(self.file_name, "w", 0)
			self.log.write("# Short log updated " + str(datetime.datetime.now()) + "\n")	
			LogFile.setup(self, game.board, game.players)

		elif self.phase == 1:
			for message in self.logged[len(self.logged)-2:]:
				self.log.write(str(message[0]) + " : " + message[1] + "\n")

		self.phase = (self.phase + 1) % 2		
		
	def close(self):
		if self.phase == 1:
			ending = self.logged[len(self.logged)-1]
			self.log.write(str(ending[0]) + " : " + ending[1] + "\n")
		self.log.write("# EOF\n")
		if self.log != sys.stdout:
			self.log.close()
		

class HeadRequest(urllib2.Request):
	def get_method(self):
		return "HEAD"

class HttpGetter(StoppableThread):
	def __init__(self, address):
		StoppableThread.__init__(self)
		self.address = address
		self.log = urllib2.urlopen(address)
		self.lines = []
		self.lock = threading.RLock() #lock for access of self.state
		self.cond = threading.Condition() # conditional

	def run(self):
		while not self.stopped():
			line = self.log.readline()
			if line == "":
				date_mod = datetime.datetime.strptime(self.log.headers['last-modified'], "%a, %d %b %Y %H:%M:%S GMT")
				self.log.close()
	
				next_log = urllib2.urlopen(HeadRequest(self.address))
				date_new = datetime.datetime.strptime(next_log.headers['last-modified'], "%a, %d %b %Y %H:%M:%S GMT")
				while date_new <= date_mod and not self.stopped():
					next_log = urllib2.urlopen(HeadRequest(self.address))
					date_new = datetime.datetime.strptime(next_log.headers['last-modified'], "%a, %d %b %Y %H:%M:%S GMT")
				if self.stopped():
					break

				self.log = urllib2.urlopen(self.address)
				line = self.log.readline()

			self.cond.acquire()
			self.lines.append(line)
			self.cond.notifyAll()
			self.cond.release()

			#sys.stderr.write(" HttpGetter got \'" + str(line) + "\'\n")

		self.log.close()
				
				
	
		
		
class HttpReplay():
	def __init__(self, address):
		self.getter = HttpGetter(address)
		self.getter.start()
		
	def readline(self):
		self.getter.cond.acquire()
		while len(self.getter.lines) == 0:
			self.getter.cond.wait()
			
		result = self.getter.lines[0]
		self.getter.lines = self.getter.lines[1:]
		self.getter.cond.release()

		return result
			
			
	def close(self):
		self.getter.stop()

class FileReplay():
	def __init__(self, filename):
		self.f = open(filename, "r", 0)
		self.filename = filename
		self.mod = os.path.getmtime(filename)
		self.count = 0
	
	def readline(self):
		line = self.f.readline()
		
		while line == "":
			mod2 = os.path.getmtime(self.filename)
			if mod2 > self.mod:
				#sys.stderr.write("File changed!\n")
				self.mod = mod2
				self.f.close()
				self.f = open(self.filename, "r", 0)
				
				new_line = self.f.readline()
				
				if " ".join(new_line.split(" ")[0:3]) != "# Short log":
					for i in range(self.count):
						new_line = self.f.readline()
						#sys.stderr.write("Read back " + str(i) + ": " + str(new_line) + "\n")
					new_line = self.f.readline()
				else:
					self.count = 0
				
				line = new_line

		self.count += 1
		return line

	def close(self):
		self.f.close()
		
						
def log(s):
	for l in log_files:
		l.write(s)
		

def log_init(board, players):
	for l in log_files:
		l.setup(board, players)

