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
 * @param new_type_index - Index for initial type of piece
 * @param new_piece_index - Index for piece in a vector
 */
Piece::Piece(int new_x, int new_y, const Piece::Colour & new_colour, const Piece::Type & type1, const Piece::Type & type2, 
	     int new_type_index)
	: x(new_x), y(new_y), colour(new_colour), type_index(new_type_index), types(), current_type()
{
	types[0] = type1; types[1] = type2;
	if (type_index < 0 || type_index >= 2)
	{
		current_type = Piece::UNKNOWN;
	}
	else
	{
		current_type = types[type_index];
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
	: white(), black(), white_unknown(), black_unknown(), white_nUnknown(0), black_nUnknown(0),
	white_king(NULL), black_king(NULL)
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
	Piece::Colour colours[] = {Piece::BLACK, Piece::WHITE};
	Piece::Type types[] = {Piece::PAWN, Piece::BISHOP, Piece::KNIGHT, Piece::ROOK, Piece::QUEEN};

	// frequency of each type of piece
	map<Piece::Type, int> freq;
	freq[Piece::ROOK] = 2;
	freq[Piece::BISHOP] = 2;
	freq[Piece::KNIGHT] = 2;
	freq[Piece::QUEEN] = 1;
	freq[Piece::PAWN] = 8;
	
	if (!choose_types)
	{
		white_unknown = freq;
		black_unknown = freq;
		white_nUnknown = 15;
		black_nUnknown = 15;
	}
	
	// for white and black...
	for (int i = 0; i < 2; ++i)
	{
		vector<Piece*> & v = pieces(colours[i]); // get vector of pieces
		
		

		// add pawns
		int y = (i == 0) ? 1 : BOARD_HEIGHT-2;
		for (int x = 0; x < BOARD_WIDTH; ++x)
		{	
			Piece::AddPiece(v, x, y, colours[i], Piece::PAWN, Piece::UNKNOWN);
		}		

		// add other pieces
		y = (i == 0) ? 0 : BOARD_HEIGHT-1;
		Piece::AddPiece(v, 0, y, colours[i], Piece::ROOK, Piece::UNKNOWN);
		Piece::AddPiece(v, BOARD_WIDTH-1, y, colours[i], Piece::ROOK, Piece::UNKNOWN);
		Piece::AddPiece(v, 1, y, colours[i], Piece::KNIGHT, Piece::UNKNOWN);
		Piece::AddPiece(v, BOARD_WIDTH-2, y, colours[i], Piece::KNIGHT, Piece::UNKNOWN);
		Piece::AddPiece(v, 2, y, colours[i], Piece::BISHOP, Piece::UNKNOWN);
		Piece::AddPiece(v, BOARD_WIDTH-3, y, colours[i], Piece::BISHOP, Piece::UNKNOWN);
		Piece::AddPiece(v, 3, y, colours[i], Piece::QUEEN, Piece::UNKNOWN);

		Piece * k = Piece::AddPiece(v, 4, y, colours[i], Piece::KING, Piece::KING, 1);
		if (i == 0)
			white_king = k;
		else
			black_king = k;
		
		
		// add to board and choose second types if required
		map<Piece::Type, int> f(freq); 
		int type2;
		for (unsigned j = 0; j < v.size(); ++j)
		{
			Piece * p = v[j];
			grid[p->x][p->y].piece = p;
			if (choose_types)
			{
				if (p->types[1] != Piece::UNKNOWN)
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
 * @param cpy - Board to clone
 */
Board::Board(Board & cpy) 
: white(cpy.white), black(cpy.black), white_unknown(cpy.white_unknown), black_unknown(cpy.black_unknown), 
  white_nUnknown(cpy.white_nUnknown), black_nUnknown(cpy.black_nUnknown), 
  white_king(cpy.white_king), black_king(cpy.black_king)
{
	for (int x = 0; x < BOARD_WIDTH; ++x)
	{
		for (int y = 0; y < BOARD_HEIGHT; ++y)
		{
			grid[x][y].x = x;
			grid[x][y].y = y;
			if (cpy.grid[x][y].piece != NULL)
			{
				vector<Piece*> & v = pieces(cpy.grid[x][y].piece->colour);
				Piece::AddPiece(v, *(cpy.grid[x][y].piece));
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
 * @param type - Type of the Piece as a string
 */
void Board::Update_select(int x, int y, int index, const string & type)
{
	Board::Update_select(x, y, index, Piece::str2type(type));
}

/**
 * @funct Update_select
 * @purpose Update Piece that has been selected
 * @param x, y - Position of Piece to update
 * @param index - 0 or 1 - State the Piece "collapsed" into
 * @param t - Type of the Piece
 */
void Board::Update_select(int x, int y, int index, const Piece::Type & t)
{
	cerr << "Updating " << x << "," << y << " " << grid[x][y].piece << " " << index << " " << t << "\n";
	Square & s = grid[x][y];
	
	
	
	assert(s.piece != NULL);
	assert(index >= 0 && index < 2);
	s.piece->type_index = index;
	
	if (s.piece->types[index] == Piece::UNKNOWN)
	{
		map<Piece::Type, int> & m = unknown_types(s.piece->colour);
		int n = (m[t]--);
		if (n < 0)
			throw Exception("Board::Update_select", "Too many pieces of type %s found", Piece::type2str(t));
		
		nUnknown(s.piece->colour)--;
		
	}
	s.piece->types[index] = t;
	s.piece->current_type = t;
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
			if (k->colour == Piece::WHITE)
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
	assert(p->current_type != Piece::UNKNOWN);
	
	int x = p->x; int y = p->y;
	if (p->current_type == Piece::KING)
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
	else if (p->current_type == Piece::KNIGHT)
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
	else if (p->current_type == Piece::PAWN)
	{
		int y1 = (p->colour == Piece::WHITE) ? BOARD_HEIGHT-2 : 1;
		int y2 = (p->colour == Piece::WHITE) ? y1 - 2 : y1 + 2;
		if (p->types[0] == Piece::PAWN && p->y == y1)
		{
			
			Move(p, x, y2, v);
		}
		y2 = (p->colour == Piece::WHITE) ? y - 1 : y + 1;
		Move(p, x, y2, v);

		if (Valid_position(x-1, y2) && grid[x-1][y2].piece != NULL)
			Move(p, x-1, y2, v);
		if (Valid_position(x+1, y2) && grid[x+1][y2].piece != NULL)
			Move(p, x+1, y2, v);
	}
	else if (p->current_type == Piece::BISHOP)
	{
		Scan(p, 1, 1, v);
		Scan(p, 1, -1, v);
		Scan(p, -1, 1, v);
		Scan(p, -1, -1, v);
	}
	else if (p->current_type == Piece::ROOK)
	{
		Scan(p, 1, 0, v);
		Scan(p, -1, 0, v);
		Scan(p, 0, 1, v);
		Scan(p, 0, -1, v);
	}
	else if (p->current_type == Piece::QUEEN)
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
		if (grid[x][y].piece != NULL)
			break;
		x += vx;
		y += vy;
	}
}

/**
 * @funct str2type
 * @purpose Convert string to Piece::Type
 * @param str - The string
 * @returns A Piece::Type
 */
Piece::Type Piece::str2type(const string & str)
{
	if (str == "king")
		return Piece::KING;
	else if (str == "queen")
		return Piece::QUEEN;
	else if (str == "rook")
		return Piece::ROOK;
	else if (str == "bishop")
		return Piece::BISHOP;
	else if (str == "knight")
		return Piece::KNIGHT;
	else if (str == "pawn")
		return Piece::PAWN;
	else if (str == "unknown")
		return Piece::UNKNOWN;

	throw Exception("Piece::str2type", "String \"%s\" doesn't represent a type", str.c_str());
	return Piece::UNKNOWN;
}

/**
 * @funct type2str
 * @purpose Convert Piece::Type to string
 * @param t - The Types
 * @returns a const char*
 */
const char * Piece::type2str(const Piece::Type & t)
{
	switch (t)
	{
		case PAWN:
			return "pawn";
		case BISHOP:
			return "bishop";
		case KNIGHT:
			return "knight";
		case ROOK:
			return "rook";
		case QUEEN:
			return "queen";
		case UNKNOWN:
			return "unknown";
		case KING:
			return "king";
		default:
			throw Exception("Piece::type2str", "Unknown type %d", (int)t);
			return "";
	}
}

/**
 * @funct str2colour
 * @purpose Convert string to Piece::Colour
 * @param str - The string
 * @returns A Piece::Colour
 */
Piece::Colour Piece::str2colour(const string & str)
{
	if (str == "white")
		return Piece::WHITE;
	else if (str == "black")
		return Piece::BLACK;

	throw Exception("Piece::str2colour", "string \"%s\" is not white|black", str.c_str());
	return Piece::BLACK; // should never get here
}

/**
 * @funct AddPiece
 * @purpose Creates a new Piece and adds it to a vector
 * @param v - The vector
 * @params - All remaining parameters passed to Piece::Piece
 * @returns Pointer to the new Piece
 */
Piece * Piece::AddPiece(vector<Piece*> & v, int x, int y, const Piece::Colour & colour, const Piece::Type & t1, const Piece::Type & t2,
			int type_index)
{
	Piece * p = new Piece(x,y,colour,t1, t2,type_index);
	v.push_back(p);
	return p;
}

/**
 * @funct AddPiece
 * @purpose Copy a Piece and add it to a vector
 * @param v - The vector
 * @param cpy - Piece to copy
 * @returns Pointer to the new Piece
 */
Piece * Piece::AddPiece(vector<Piece*> & v, const Piece & cpy)
{
	Piece * p = new Piece(cpy);
	v.push_back(p);
	return p;
}