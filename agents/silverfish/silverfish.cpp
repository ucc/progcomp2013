#include "silverfish.h"

using namespace std;

Silver::Silver(const string & colour) : Agent(colour), values()
{
	values[Piece::PAWN] = 1;
	values[Piece::BISHOP] = 3;
	values[Piece::KNIGHT] = 3;
	values[Piece::ROOK] = 5;
	values[Piece::QUEEN] = 9;
	values[Piece::KING] = 100;
	values[Piece::UNKNOWN] = 1.5;
}

Silver::Silver(const string & colour, const map<Piece::Type, double> & new_values) : Agent(colour), values(new_values)
{
	//TODO: Assert map is valid
}

Square & Silver::Select()
{
	
	return Agent::Select();
}

Square & Silver::Move()
{
	return Agent::Move();
}