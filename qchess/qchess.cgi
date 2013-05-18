#!/usr/bin/python

# CGI wrapper to qchess

import sys
import os

import cgi
import subprocess
import time
import threading


def open_fifo(name, mode, timeout=None):
	if timeout == None:
		return open(name, mode)
	
	
	class Worker(threading.Thread):
		def __init__(self):
			threading.Thread.__init__(self)
			self.result = None
			
		def run(self):		
			self.result = open(name, mode)
		

	w = Worker()
	w.start()
	
	start = time.time()
	while time.time() - start < timeout:
		if w.is_alive() == False:
			w.join()
			return w.result
		time.sleep(0.1)
	
	
	if w.is_alive():
		#sys.stderr.write("FIFO_TIMEOUT!\n")
		if mode == "r":
			f = open(name, "w")
		else:
			f = open(name, "r")
			
		#sys.stderr.write("Opened other end!\n")
		while w.is_alive():
			time.sleep(0.1)
			
		w.join()
		f.close()
		w.result.close()
		raise Exception("FIFO_TIMEOUT")
	else:
		w.join()
		return w.result

def quit():
	try:
		fifo_out = open_fifo("../cgi-data/"+client+".in", "w", 5)
	except:
		pass
	else:
		fifo_out.write("quit\n")
		fifo_out.close()
		
	try:
		fifo_in = open_fifo("../cgi-data/"+client+".out", "w", 5)
	except:
		pass
	else:
		s = fifo_in.readline().strip(" \r\n")
		while s != "":
			#print s
			s = fifo_in.readline().strip(" \r\n")
			fifo_in.close()
	time.sleep(0.5)
	
	


def main(argv):
	global client
	#form = cgi.FieldStorage()
	#client = cgi.escape(os.environ["REMOTE_ADDR"])
	
	client = "127.0.0.1"
	
	
	print "Content-Type: text/plain\r\n\r\n"

	
	try:
		request = argv[1]
	except:
		request = None

	
	try:
		x = int(argv[1])	
		y = int(argv[2])
	except:
		if request == "quit":
			quit()
			return 0
		
		if os.path.exists("../cgi-bin/"+client+".in") and os.path.exists("../cgi-bin/"+client+".out"):
			print "Error: Game in progress expects x and y"
			return 1
		else:
			print "NEW GAME"
			args = ["./qchess.py"]
			if request == None:
				args += ["@fifo:../cgi-data/"+client, "@internal:AgentBishop"]
			elif request == "eigengame":
				args += ["--server=progcomp.ucc.asn.au", "@fifo:../cgi-data/"+client]
			subprocess.Popen(args)
			time.sleep(1)
			
	else:
		
		fifo_out = open_fifo("../cgi-data/"+client+".in", "w")
		fifo_out.write("%d %d\n" % (x, y))
		fifo_out.close()
		
		
	
	sys.stderr.write("\ncgi read from fifo here\n")
	try:
		fifo_in = open_fifo("../cgi-data/"+client+".out", "r")
	except:
		quit()
	else:
		sys.stderr.write("Opened fine\n")
		s = fifo_in.readline().strip(" \r\n")
	
		while s != "SELECT?" and s != "MOVE?" and s.split(" ")[0] not in ["white", "black"]:
			if s != "":
				print s
			s = fifo_in.readline().strip(" \r\n")
		print s
		fifo_in.close()
		if s.split(" ")[0] in ["white", "black"]:
			quit()
	
	sys.stderr.write("Done\n")
	return 0


if __name__ == "__main__":
	try:
		sys.exit(main(sys.argv))
	except Exception, e:
		print "Exception: ", e
		sys.exit(1)
