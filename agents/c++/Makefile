#Makefile for C++ agent
CXX = g++ -std=gnu++0x -Wall -Werror -pedantic -g
OBJ = qchess.o agent.o main.o
LIB = 

LINKOBJ = $(OBJ)

RM = rm -f
BIN = agent++



$(BIN) : $(LINKOBJ)
	$(CXX) -o $(BIN) $(LINKOBJ)

%.o : %.cpp
	$(CXX) -c $<

no_main : $(OBJ)

main.o : main.cpp
	$(CXX) -c main.cpp

clean :
	$(RM) $(BIN) $(OBJ) $(LINKOBJ)

clean_full: #cleans up all backup files
	$(RM) $(BIN) $(OBJ) $(LINKOBJ)
	$(RM) *.*~
	$(RM) *~


	