#!/usr/bin/python -u

# CGI wrapper to qchess

import sys
import os

import cgi
import time
import threading
import datetime
import subprocess

path = "../qchess-cgi-data/"

def open_fifo(name, mode, timeout=None):
	if timeout == None:
		return open(name, mode)
	
	
	class Worker(threading.Thread):
		def __init__(self):
			threading.Thread.__init__(self)
			self.result = None
			self.exception = None

			
		def run(self):		
			try:
				self.result = open(name, mode)
			except Exception, e:
				self.exception = e
				self.result = None
		

	w = Worker()
	w.start()
	
	start = time.time()
	while time.time() - start < timeout:
		if w.is_alive() == False:
			w.join()
			if w.exception != None:
				raise w.exception
			return w.result
		time.sleep(0.1)
	
	
	if w.is_alive():
		#sys.stderr.write("FIFO_TIMEOUT!\n")
		# Recursive to deal with possible race condition
		try:
			if mode == "r":
				f = open_fifo(name, "w", 1)
			else:
				f = open_fifo(name, "r", 1)
		except:
			pass
			
		#sys.stderr.write("Opened other end!\n")
		while w.is_alive():
			time.sleep(0.1)
			
		w.join()
		f.close()
		w.result.close()
		raise Exception("FIFO_TIMEOUT")
	else:
		w.join()
		if w.exception != None:
			raise w.exception
		return w.result

def force_quit():
	os.remove(path+client+".in")
	os.remove(path+client+".out")

def quit():
	
	if os.path.exists(path+client+".in") and os.path.exists(path+client+".out"):
		try:
			fifo_out = open_fifo(path+client+".in", "w", 5)
		except:
			pass
		else:
			if fifo_out != None:
				fifo_out.write("quit\n")
				fifo_out.close()
		
		try:
			fifo_in = open_fifo(path+client+".out", "r", 5)
		except:
			pass
		else:
			if fifo_in != None:
				s = fifo_in.readline().strip(" \r\n")
				while s != "":
			#print s
					s = fifo_in.readline().strip(" \r\n")
					fifo_in.close()
			
	log = open(path+client, "a")
	log.write(" -> %s\n" % str(datetime.datetime.now()))
	log.close()
			
	time.sleep(0.5)
	
	


def main(argv):
	print "Content-Type: text/plain\r\n" #Removed the second new line. Makes parsing everything easier ~BG3
	
	global client
	form = cgi.FieldStorage()
	client = cgi.escape(os.environ["REMOTE_ADDR"])
	
	#client = "127.0.0.1"
	
	
	

	
	try:
		#request = argv[1]
		request = form["r"].value
	except:
		request = None
		mode = None
	else:
		try:
			mode = form["m"].value
		except:
			mode = None
	

	
	try:
		#x = int(argv[1])	
		#y = int(argv[2])
		x = int(form["x"].value)
		y = int(form["y"].value)
	except:
		if request == "force_quit":
			force_quit()
			quit()
			return 0

		if os.path.exists(path+client+".in") and os.path.exists(path+client+".out"):
			if request == "quit":
				print "Quit."
				quit()
				return 0
			
			print "Game in progress expects x and y."
			return 1
		elif request == "start":
			print "New game."
			args = path+"qchess.py --no-graphics"
			if mode == "black":
				args += " @internal:AgentBishop @fifo:../qchess-cgi-data/"+client
			elif mode == None or mode == "bishop":
				args += " @fifo:../qchess-cgi-data/"+client+" @internal:AgentBishop"
			elif mode == "random":
				args += " @fifo:../qchess-cgi-data/"+client+" @internal:AgentRandom"
			elif mode == "eigengame":
				args += " --server=progcomp.ucc.asn.au @fifo:../qchess-cgi-data/"+client

			args += " --log=@../qchess-cgi-data/"+client+".log";

			os.system("echo '"+args+"' | at now")

		#	subprocess.Popen(args)
		#	os.spawnl(os.P_NOWAIT, args)


			time.sleep(1)
			
			log = open(path+client, "a")
			log.write("%s" % str(datetime.datetime.now()))
			log.close()
			
		else:
			print "No game in progress."
			return 1
			
	else:
		if not (os.path.exists(path+client+".in") and os.path.exists(path+client+".out")):
			print "No game in progress."
			return 1
			
		try:
			fifo_out = open_fifo(path+client+".in", "w")
		except:
			quit()
		else:
			fifo_out.write("%d %d\n" % (x, y))
			fifo_out.close()
		
		
	
	#sys.stderr.write("\ncgi read from fifo here\n")
	try:
		fifo_in = open_fifo(path+client+".out", "r")
	except:
		quit()
	else:
		#	sys.stderr.write("cgi opened fine\n")
		s = fifo_in.readline().strip(" \r\n")
		#sys.stderr.write("cgi read first line: "+str(s)+"\n")	
		while s != "SELECT?" and s != "MOVE?" and not s.split(" ")[0] in ["white","black"]:
			if s != "":
				print s
		#	sys.stderr.write("Read: " + str(s) + "\n")
			
			s = fifo_in.readline().strip(" \r\n")
		print s
		fifo_in.close()
		if s.split(" ")[0] in ["white", "black"]:
			#sys.stderr.write("cgi quit!\n")
			quit()
	
	#sys.stderr.write("cgi qchess Done\n")
	return 0


if __name__ == "__main__":
	try:
		sys.exit(main(sys.argv))
	except Exception, e:
		print e
		sys.stderr.write(sys.argv[0] + ": " + str(e) + "\n")
		sys.exit(1)
