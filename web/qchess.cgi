#!/usr/bin/python

# CGI wrapper to qchess

import sys
import os

import cgi
import subprocess

def main(argv):
	form = cgi.FieldStorage()
	client = cgi.escape(os.environ["REMOTE_ADDR"])
	
	print "Content-Type: text/plain\r\n\r\n"
	
	try:
		with open(client): pass
	except IOError:
		args = ["python", "../qchess/qchess.py", "--no-graphics", "@fifo:"+client, "@internal:AgentBishop"]
		subprocess.Popen(args)
		form["mode"] = "query"
	
	if form["mode"] == "response":
		x = int(form["x"])
		y = int(form["y"])
		fifo_out = open(client+".in", "w")
		fifo_out.write("%d %d\n" % (x, y))
		fifo_out.close()
		form["mode"] = "query"
	
		
	if form["mode"] == "query":
		fifo_in = open(client+".out", "r")
		s = fifo_in.readline().strip(" \r\n")
		while s != "SELECT?" and s != "MOVE?" and s.split(" ")[0] != "white" and s.split(" ")[0] != "black":
			print s
			s = fifo_in.readline().strip(" \r\n")
		print s
		fifo_in.close()
		form["mode"] = "response"
		
		if s == "quit":
			os.remove(client)
			
		
	return 0


if __name__ == "__main__":
	try:
		sys.exit(main(sys.argv))
	except, e:
		print "Exception: ", e
		sys.exit(1)
