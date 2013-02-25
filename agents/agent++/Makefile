# Makefile for agent++

CXX = g++ -std=gnu++0x -g -Werror -Wall -pedantic 
LINK_OBJ = qchess.o agent.o main.o


BIN = agent++

$(BIN) : $(LINK_OBJ)
	$(CXX) -o $(BIN) $(LINK_OBJ) 

%.o : %.c
	$(CXX) $(FLAGS) -c $<

clean :
	$(RM) $(BIN) $(OBJ) $(LINK_OBJ)

clean_full: #cleans up all backup files
	$(RM) $(BIN) $(OBJ) $(LINK_OBJ)
	$(RM) *.*~
	$(RM) *~
