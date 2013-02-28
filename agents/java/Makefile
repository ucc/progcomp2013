# Q: WHY IS THERE A MAKEFILE FOR A JAVA PROGRAM???
# A: Because Java doesn't like running programs from different directories. I have to do that.
#	... so I compile the Java program into an executable with gcj, and then I can run it from whatever directory I want.

SRC = Agent.java Reader.java Piece.java Board.java Square.java
MAIN = Agent
BIN = cough

$(BIN) : $(SRC)
	gcj -o $(BIN) --main=$(MAIN) $(SRC)


clean : 
	rm -f $(BIN)
	rm -f *.class
	rm -f *~


