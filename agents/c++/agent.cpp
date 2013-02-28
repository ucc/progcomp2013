/**
 * agent++ : A Sample agent for UCC::Progcomp2013
 * @file agent.cpp
 * @purpose Definition of Agent class
 */

#include "agent.h"
#include <cassert> // for sanity checks

using namespace std;

/**
 * @constructor Agent
 * @param new_colour - colour of the Agent
 */
Agent::Agent(const string & new_colour) : colour(Piece::str2colour(new_colour)), board(), selected(NULL)
{

}

/**
 * @destructor ~Agent
 */
Agent::~Agent()
{

}

/**
 * @funct Select
 * @purpose Selects a piece at random
 * @returns Square containing the selected piece
 */
Square & Agent::Select()
{
	vector<Piece*> & v = board.pieces(colour); // get pieces
	int choice = rand() % v.size(); // pick random index
	Piece * p = v[choice]; // get piece at the index
	assert(p->colour == colour);
	selected = p; // update selected
	//cerr << "Selected " << p->x << "," << p->y << " [" << p->types[0] << "," << p->types[1] << "]\n";
	return board.square(p->x, p->y); // get Square from board
}

/**
 * @funct Move
 * @purpose Pick a square to move a selected piece into
 * @returns Square to move last selected piece into
 */
Square & Agent::Move()
{
	assert(selected != NULL);
	vector<Square*> moves; // all possible moves for selected piece
	board.Get_moves(selected, moves); // populate possible moves
	assert(moves.size() > 0); 
	int choice = rand() % moves.size(); // pick random index
	return *(moves[choice]); // return that move
}

/**
 * @funct Run
 * @purpose The "Game Loop" for the agent; read commands and call appropriate function to make responses
 * @param in - Stream to read input from (use std::cin)
 * @param out - Stream to write output to (use std::cout)
 */
void Agent::Run(istream & in, ostream & out)
{
	string cmd; // buffer for tokens
	while (in.good())
	{
		in >> cmd; // read first token only
		if (cmd == "QUIT")
		{
			break;
		}
		else if (cmd == "SELECTION?")
		{
			Square & s = Select(); // get selection
			out << s.x << " " << s.y  << "\n"; // return response through output
		}
		else if (cmd == "MOVE?")
		{
			Square & s = Move(); // get move
			out << s.x << " " << s.y << "\n"; // return response through output
		}
		else
		{
			// There were multiple tokens...
			stringstream s(cmd);
			int x; int y;
			s >> x; // Convert first token (in cmd) to an int
			in >> y; // Read second token from in
			
			in >> cmd; // Read third token
			
			if (cmd == "->") // Token indicates a move was made
			{
				int x2; int y2; // remaining two tokens indicate destination
				in >> x2; in >> y2;
				board.Update_move(x, y, x2, y2); // update the board
			}
			else
			{
				// Tokens are for a selection
				int index; stringstream s2(cmd); 
				s2 >> index; // convert third token to an index
				in >> cmd; // Read fourth token - the new type of the piece
				board.Update_select(x, y, index, cmd); // update the board
			}
			
		}
	}
}
