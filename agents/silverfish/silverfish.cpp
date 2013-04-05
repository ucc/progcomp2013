#include "silverfish.h"

using namespace std;



bool sort_scores(pair<Square*, double> & a, pair<Square*, double> & b)
{
	return 	a.second > b.second;
}


Silver::Silver(const string & colour, int new_max_depth) : Agent(colour),  values(), max_depth(new_max_depth), depth(0),
{
	values[Piece::PAWN] = 1;
	values[Piece::BISHOP] = 3;
	values[Piece::KNIGHT] = 3;
	values[Piece::ROOK] = 5;
	values[Piece::QUEEN] = 9;
	values[Piece::KING] = 100;
	values[Piece::UNKNOWN] = 1.5;
}

Silver::Silver(const string & colour, const map<Piece::Type, double> & new_values, int new_max_depth) 
	: Agent(colour), values(new_values), max_depth(new_max_depth), depth(0)
{
	//TODO: Assert map is valid
}

Move Silver::BestMove(Piece::Colour c)
{
	
}

Square & Silver::Select()
{
	
	
	for (int x = 0; x < BOARD_WIDTH; ++x)
	{
		for (int y = 0; y < BOARD_HEIGHT; ++y)
		{
			Square & s = board.SquareAt(x,y);
			
			if (s.piece != NULL && s.piece.colour == colour)
				continue;
			
			map<Piece*, double> m = board.SquareAt(x,y).Coverage(colour);	
			
			for (map<Piece*, double>::iterator i = m.begin(); i != m.end(); ++i)
			{
				moves[i->first].push_back(pair<Square*, double>
			}
		}
	}
	
	for (map<Piece*, vector<pair<Square*, double> > >::iterator i = moves.begin(); i < moves.end()
	
}

Square & Silver::Move()
{
	vector<Square*> moves;
	board.Get_moves(selected);
}

double ScoreMove(Piece * p, Square & target)
{
	++depth;
	double score = 0.0;
	if (target.piece == NULL)
		score = 0.0
	else
		score = 0.5*(values[target.piece->types[0]] + values[target.piece->types[1]]);
	
	if (depth < max_depth)
	{
		double recurse_score;
		
		BestMove(Piece::Opposite(p->colour));
	}
	--depth;
	return score;
}