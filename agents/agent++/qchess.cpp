/**
 * agent++ : A Sample agent for UCC::Progcomp2013
 * @file qchess.h
 * @purpose Definitions for game related classes; Piece, Square, Board
 */

#include "qchess.h"
#include <cassert>

using namespace std;

/**
 * @constructor
 * @param new_x, new_y - Position of piece
 * @param new_colour - Colour of piece
 * @param type1, type2 - Types of piece
 * @param index - Index for initial type of piece
 */
Piece::Piece(int new_x, int new_y, const string & new_colour, const string & type1, const string & type2, int index)
	: x(new_x), y(new_y), colour(new_colour), type_index(index), types(), current_type()
{
	types[0] = type1; types[1] = type2;
	if (index < 0 || index >= 2)
	{
		current_type = "unknown";
	}
	else
	{
		current_type = types[index];
	}
}

/**
 * @constructor
 * @param cpy - Piece to copy construct from
 */
Piece::Piece(const Piece & cpy) : x(cpy.x), y(cpy.y), colour(cpy.colour), type_index(cpy.type_index)
{
	types[0] = cpy.types[0];
	types[1] = cpy.types[1];
}

/**
 * @constructor
 * @param choose_types - Indicates whether Board should setup the 2nd types of pieces; default false
 */
Board::Board(bool choose_types)
{

	// initialise all the Squares
	for (int x = 0; x < BOARD_WIDTH; ++x)
	{
		for (int y = 0; y < BOARD_HEIGHT; ++y)
		{
			grid[x][y].x = x;
			grid[x][y].y = y;
		}
	}

	// const arrays simplify below code
	string colours[] = {"black", "white"};
	string types[] = {"rook", "bishop", "knight", "queen", "pawn"};

	// frequency of each type of piece
	map<string, int> freq;
	freq["rook"] = 2;
	freq["bishop"] = 2;
	freq["knight"] = 2;
	freq["queen"] = 1;
	freq["pawn"] = 8;
	
	// for white and black...
	for (int i = 0; i < 2; ++i)
	{
		vector<Piece*> & v = pieces(colours[i]); // get vector of pieces
		
		

		// add pawns
		int y = (i == 0) ? 1 : BOARD_HEIGHT-2;
		for (int x = 0; x < BOARD_WIDTH; ++x)
		{	
			Piece * p = new Piece(x, y, colours[i], "pawn", "unknown");
			v.push_back(p);
		}		

		// add other pieces
		y = (i == 0) ? 0 : BOARD_HEIGHT-1;
		v.push_back(new Piece(0, y, colours[i], "rook", "unknown"));
		v.push_back(new Piece(BOARD_WIDTH-1, y, colours[i], "rook", "unknown"));
		v.push_back(new Piece(1, y, colours[i], "knight", "unknown"));
		v.push_back(new Piece(BOARD_WIDTH-2, y, colours[i], "knight", "unknown"));
		v.push_back(new Piece(2, y, colours[i], "bishop", "unknown"));
		v.push_back(new Piece(BOARD_WIDTH-3, y, colours[i], "bishop", "unknown"));
		v.push_back(new Piece(3, y, colours[i], "queen", "unknown"));

		Piece * k = new Piece(4, y, colours[i], "king", "king", 1);
		if (i == 0)
			white_king = k;
		else
			black_king = k;
		v.push_back(k);
		
		// add to board and choose second types if required
		map<string, int> f(freq); 
		int type2;
		for (unsigned j = 0; j < v.size(); ++j)
		{
			Piece * p = v[j];
			grid[p->x][p->y].piece = p;
			if (choose_types)
			{
				if (p->types[1] != "unknown")
					continue;
	
				do
				{
					type2 = rand() % 5;
				} while (f[types[type2]] <= 0);
				f[types[type2]] -= 1;
	
				p->types[1] = types[type2];			
			}

			
		}

		

	}

}

/**
 * @constructor
 * @param cpy - Board to copy construct from; each Piece in the copy will be *copied*
 *		The Piece's in the copied Board may be altered without affecting the original
 */
Board::Board(const Board & cpy)
{
	for (int x = 0; x < BOARD_WIDTH; ++x)
	{
		for (int y = 0; y < BOARD_HEIGHT; ++y)
		{
			grid[x][y].x = x;
			grid[x][y].y = y;

			if (cpy.grid[x][y].piece != NULL)
			{
				grid[x][y].piece = new Piece(*(cpy.grid[x][y].piece));
				pieces(grid[x][y].piece->colour).push_back(grid[x][y].piece);
			}
		}
	}
}

/**
 * @destructor
 */
Board::~Board()
{
	white.clear();
	black.clear();
	for (int x = 0; x < BOARD_WIDTH; ++x)
	{
		for (int y = 0; y < BOARD_HEIGHT; ++y)
		{
			delete grid[x][y].piece;
		}
	}

}

/**
 * @funct Update_select
 * @purpose Update Piece that has been selected
 * @param x, y - Position of Piece to update
 * @param index - 0 or 1 - State the Piece "collapsed" into
 * @param type - Type of the Piece
 */
void Board::Update_select(int x, int y, int index, const string & type)
{
	cerr << "Updating " << x << "," << y << " " << grid[x][y].piece << " " << index << " " << type << "\n";
	Square & s = grid[x][y];
	assert(s.piece != NULL);
	assert(index >= 0 && index < 2);
	s.piece->type_index = index;
	s.piece->types[index] = type;
	s.piece->current_type = type;
}

/**
 * @funct Update_move
 * @purpose Move a Piece from one square to another
 * @param x1, y1 - Coords of Square containing moving Piece
 * @param x2, y2 - Coords of Square to move into
 * 	NOTE: Any Piece in the destination Square will be destroyed ("taken")
 *		and the Board's other members updated accordingly
 */
void Board::Update_move(int x1, int y1, int x2, int y2)
{
	Square & s1 = grid[x1][y1];
	Square & s2 = grid[x2][y2];
	if (s2.piece != NULL)
	{
		vector<Piece*> & p = pieces(s2.piece->colour);
		vector<Piece*>::iterator i = p.begin();
		while (i != p.end())
		{
			if (*i == s2.piece)
			{
				p.erase(i);
				break;
			}
			++i;
		}
		Piece * k = king(s2.piece->colour);
		if (k == s2.piece)
		{
			if (k->colour == "white")
				white_king = NULL;
			else
				black_king = NULL;
		}

		delete s2.piece;
	}	

	s1.piece->x = s2.x;
	s1.piece->y = s2.y;

	s2.piece = s1.piece;
	s1.piece = NULL;	
}

/**
 * @funct Get_moves
 * @purpose Get all moves for a Piece and store them
 * @param p - Piece
 * @param v - vector to store Squares in. Will *not* be cleared.
 */
void Board::Get_moves(Piece * p, vector<Square*> & v)
{
	assert(p->current_type != "unknown");
	int x = p->x; int y = p->y;
	if (p->current_type == "king")
	{
		Move(p, x+1, y, v);
		Move(p, x-1, y, v);
		Move(p, x, y+1, v);
		Move(p, x, y-1, v);
		Move(p, x+1, y+1, v);
		Move(p, x+1, y-1, v);
		Move(p, x-1, y+1, v);
		Move(p, x-1, y-1, v);
	}
	else if (p->current_type == "knight")
	{
		Move(p, x+2, y+1, v);
		Move(p, x+2, y-1, v);
		Move(p, x-2, y+1, v);
		Move(p, x-2, y-1, v);
		Move(p, x+1, y+2, v);
		Move(p, x-1, y+2, v);
		Move(p, x+1, y-2, v);
		Move(p, x-1, y-2, v); 
	}
	else if (p->current_type == "pawn")
	{
		int y1 = (p->colour == "white") ? BOARD_HEIGHT-2 : 1;
		int y2 = (p->colour == "white") ? y1 - 2 : y1 + 2;
		if (p->types[0] == "pawn" && p->y == y1)
		{
			
			Move(p, x, y2, v);
		}
		y2 = (p->colour == "white") ? y - 1 : y + 1;
		Move(p, x, y2, v);

		if (Valid_position(x-1, y2) && grid[x-1][y2].piece != NULL)
			Move(p, x-1, y2, v);
		if (Valid_position(x+1, y2) && grid[x+1][y2].piece != NULL)
			Move(p, x+1, y2, v);
	}
	else if (p->current_type == "bishop")
	{
		Scan(p, 1, 1, v);
		Scan(p, 1, -1, v);
		Scan(p, -1, 1, v);
		Scan(p, -1, -1, v);
	}
	else if (p->current_type == "rook")
	{
		Scan(p, 1, 0, v);
		Scan(p, -1, 0, v);
		Scan(p, 0, 1, v);
		Scan(p, 0, -1, v);
	}
	else if (p->current_type == "queen")
	{
		Scan(p, 1, 1, v);
		Scan(p, 1, -1, v);
		Scan(p, -1, 1, v);
		Scan(p, -1, -1, v);
		Scan(p, 1, 0, v);
		Scan(p, -1, 0, v);
		Scan(p, 0, 1, v);
		Scan(p, 0, -1, v);
	}

} 

/**
 * @funct Move
 * @purpose Add a move to the vector, if it is valid
 * @param p - Piece that would move
 * @param x, y - Destination Square coords
 * @param v - vector to put the destination Square in, if the move is valid
 */
void Board::Move(Piece * p, int x, int y, vector<Square*> & v)
{
	if (Valid_position(x, y) && (grid[x][y].piece == NULL || grid[x][y].piece->colour != p->colour))
	{
		v.push_back(&(grid[x][y]));
	}
	//else
	//	cerr << "Square " << x << "," << y << " invalid; " << grid[x][y].piece << "\n";
}

/**
 * @funct Scan
 * @purpose Add moves in a specified direction to the vector, until we get to an invalid move
 * @param p - Piece to start scanning from
 * @param vx, vy - "velocity" - change in coords each move
 * @param v - vector to store valid Squares in
 */
void Board::Scan(Piece * p, int vx, int vy, vector<Square*> & v)
{
	int x = p->x + vx;
	int y = p->y + vy;
	while (Valid_position(x, y) && (grid[x][y].piece == NULL || grid[x][y].piece->colour != p->colour))
	{
		v.push_back(&(grid[x][y]));
		x += vx;
		y += vy;
	}
}
