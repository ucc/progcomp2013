/**
 * agent++ : A Sample agent for UCC::Progcomp2013
 * @file qchess.h
 * @purpose Declarations for game related classes; Piece, Square, Board
 */

#ifndef _QCHESS_H
#define _QCHESS_H


// board height and width (don't change!)
#define BOARD_HEIGHT 8
#define BOARD_WIDTH 8

#include <string>
#include <vector>
#include <map>
#include <cstdlib>
#include <iostream>

#include <stdarg.h>
#include <cstdio> // for vfprintf... for the Exception

class Board; //forward declaration

/**
 * @class Piece
 * @purpose Represent a quantum chess piece
 */
class Piece
{
	public:

		typedef enum {PAWN, BISHOP, KNIGHT, ROOK, QUEEN, KING, UNKNOWN} Type;
		typedef enum {WHITE=0, BLACK=1} Colour;
		
		static Type AllTypes[];
		static Colour AllColours[];
		

		virtual ~Piece() {} // destructor

		int x; int y; // position of the piece
		Colour colour; // colour of the piece
		int type_index; // indicates state the piece is in; 0, 1, or -1 (unknown)
		Type types[2]; // states of the piece
		Type current_type; // current state of the piece
		
		static Type str2type(const std::string & str);
		static Colour str2colour(const std::string & str);
		static const char * type2str(const Type & t);
		
		static Piece * AddPiece(std::vector<Piece*> & v, int x, int y, const Colour & colour, const Type & type1, const Type & type2, int type_index=-1);
		static Piece * AddPiece(std::vector<Piece*> & v, const Piece & cpy);
		
		static Colour Opposite(const Colour & c)
		{
			return (c == WHITE) ? BLACK : WHITE;	
		}
		
		double ProbIsType(Board & b, const Piece::Type & t);
		
	private:
		friend class Board;
		Piece(int x, int y, const Colour & colour, const Type & type1, const Type & type2
			, int type_index); // constructor
		Piece(const Piece & cpy); // copy constructor

		

};

/**
 * @class Square
 * @purpose Represent a Square on the board; not necessarily occupied
 */
class Square
{
	public:
		Square() : x(-1), y(-1), piece(NULL) {} // constructor
		Square(int new_x, int new_y, Piece * new_piece = NULL) : x(new_x), y(new_y), piece(new_piece) {} //UNUSED
		Square(const Square & cpy) : x(cpy.x), y(cpy.y), piece(cpy.piece) {} // copy constructor (UNUSED)
		virtual ~Square() {} //destructor
		int x;	int y; // position of the square
		Piece * piece; // Piece that is in the Square (NULL if unoccupied)
	
		const std::map<Piece*, double> & Coverage(const Piece::Colour & c)
		{
			return (c == Piece::WHITE) ? coverage[Piece::WHITE] : coverage[Piece::BLACK];
		}
		
		void Update_coverage(Board & b);
		
	private:
		std::map<Piece::Colour, std::map<Piece*, double> > coverage;
};

/**
 * @class Board
 * @purpose Represent a quantum chess board
 */
class Board
{
	public:
		Board(bool choose_types = false); // constructor
		Board(Board & parent); // clones a board, copy on write
		virtual ~Board(); // destructor


		// helper; return vector of pieces given player colour
		std::vector<Piece*> & pieces(const Piece::Colour & colour) {return ((colour == Piece::WHITE) ? white : black);}	
		// helper; return map of unidentified 2nd types for given colour
		std::map<Piece::Type, int> & unknown_types(const Piece::Colour & colour)
		{
			return ((colour == Piece::WHITE) ? white_unknown : black_unknown);
		}
		
		int & nUnknown(const Piece::Colour & colour)
		{
			return ((colour == Piece::WHITE) ? white_nUnknown : black_nUnknown);
		}
		
		// helper; return king given player colour	
		Piece * king(const Piece::Colour & colour) {return ((colour == Piece::WHITE) ? white_king : black_king);}
		
		void Update_move(int x, int y, int x2, int y2); // move a piece
		void Update_select(int x, int y, int index, const std::string & type); // update a selected piece
		void Update_select(int x, int y, int index, const Piece::Type & t);
	
		Square & square(int x, int y) {return grid[x][y];} // get square on board

		void Get_moves(Square & s, const Piece::Type & t, std::vector<Square*> & v);
		void Get_moves(Piece * p, std::vector<Square*> & v); // get allowed moves for piece of known type

		// determine if position is on the board
		bool Valid_position(int x, int y) const {return (x >= 0 && x <= BOARD_WIDTH-1 && y >= 0 && y <= BOARD_HEIGHT-1);}
		

		// scans from a square until a piece is reached
		Piece * ScanPiece(Square & s, int vx, int vy);
		
		// Get a piece
		Square & SquareAt(int x, int y);

	private:
		Square grid[BOARD_WIDTH][BOARD_HEIGHT];

		// All pieces for each player
		std::vector<Piece*> white;
		std::vector<Piece*> black;
		// The number of pieces with each 2nd type that are still unidentified
		std::map<Piece::Type, int> white_unknown; 
		std::map<Piece::Type, int> black_unknown;
		int white_nUnknown;
		int black_nUnknown;
		Piece * white_king;
		Piece * black_king;
		
		

		// Add a move to the vector if it is valid
		void CheckMove(Piece * p, int x, int y, std::vector<Square*> & v);

		// Add all valid moves in a direction, stopping at the first invalid move
		void ScanMoves(Piece * p, int vx, int vy, std::vector<Square*> & v);
		
		
};

/**
 * @class Exception
 * @purpose The only exception.
 */
class Exception
{
	public:
		Exception(const char * funct, const char * fmt, ...)
		{
			fprintf(stderr, "Exception in %s - ", funct);
			va_list va;
			va_start(va, fmt);
			vfprintf(stderr, fmt, va);
			va_end(va);
			fprintf(stderr, "\n");			
		}
	
};

#endif //_QCHESS_H

//EOF
