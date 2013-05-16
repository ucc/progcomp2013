#!/usr/bin/python

import sys
import os
import cgi


if __name__ == "__main__":
	form = cgi.FieldStorage()
	x = int(form.getvalue("x"))
	y = int(form.getvalue("y"))
	
	print "Content-type:text/html\r\n\r\n"
	print "<html>\n<head>\n<title>Webbified QChess</title>\n</head>\n<body>"
	print "<p> x = %d\ty = %d <\p>" % (x, y)
	print "</body>\n</html>"