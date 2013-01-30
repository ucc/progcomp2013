log_file = None
import datetime
import urllib2

class LogFile():
	def __init__(self, file_name):	
		
		self.log = open(file_name, "w", 0)

	def write(self, s):
		self.log.write(str(datetime.datetime.now()) + " : " + s + "\n")

	def setup(self, board, players):
		self.log.write("# Log starts " + str(datetime.datetime.now()) + "\n")
		for p in players:
			self.log.write("# " + p.colour + " : " + p.name + "\n")
		
		self.log.write("# Initial board\n")
		for x in range(0, w):
			for y in range(0, h):
				if board.grid[x][y] != None:
					self.log.write(str(board.grid[x][y]) + "\n")

		self.log.write("# Start game\n")

class HttpLog(LogFile):
	def __init__(self, file_name):
		LogFile.__init__(self, file_name)
		self.file_name = file_name

	def prelog(self):
		self.log.close()
		self.log = open(self.file_name, "w", 0)

		LogFile.setup(self, game.board, game.players)
		

class HeadRequest(urllib2.Request):
	def get_method(self):
		return "HEAD"
		
class HttpReplay():
	def __init__(self, address):
		self.read_setup = False
		self.log = urllib2.urlopen(address)
		self.address = address

	def readline(self):
		
		line = self.log.readline()
		sys.stderr.write(sys.argv[0] + " : " + str(self.__class__.__name__) + " read \""+str(line.strip("\r\n")) + "\" from address " + str(self.address) + "\n")
		if line == "":
			sys.stderr.write(sys.argv[0] + " : " + str(self.__class__.__name__) + " retrieving from address " + str(self.address) + "\n")
			date_mod = datetime.datetime.strptime(self.log.headers['last-modified'], "%a, %d %b %Y %H:%M:%S GMT")
			self.log.close()

			next_log = urllib2.urlopen(HeadRequest(self.address))
			date_new = datetime.datetime.strptime(next_log.headers['last-modified'], "%a, %d %b %Y %H:%M:%S GMT")
			while date_new <= date_mod:
				next_log = urllib2.urlopen(HeadRequest(self.address))
				date_new = datetime.datetime.strptime(next_log.headers['last-modified'], "%a, %d %b %Y %H:%M:%S GMT")

			self.log = urllib2.urlopen(self.address)
			game.setup()
			line = self.log.readline()


		return line
			
	def close(self):
		self.log.close()
						
def log(s):
	if log_file != None:
		log_file.write(s)
		

def log_init(board, players):
	if log_file != None:
		log_file.setup(board, players)

