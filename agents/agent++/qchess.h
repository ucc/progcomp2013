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

/**
 * @class Piece
 * @purpose Represent a quantum chess piece
 */
class Piece
{
	public:
		Piece(int x, int y, const std::string & new_colour, const std::string & type1 = "unknown", const std::string & type2 = "unknown", int new_type_index = -1); // constructor
		Piece(const Piece & cpy); // copy constructor
		virtual ~Piece() {} // destructor

		int x; int y; // position of the piece
		std::string colour; // colour of the piece
		int type_index; // indicates state the piece is in; 0, 1, or -1 (unknown)
		std::string types[2]; // states of the piece
		std::string current_type; // current state of the piece
		

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
};

/**
 * @class Board
 * @purpose Represent a quantum chess board
 */
class Board
{
	public:
		Board(bool choose_types = false); // constructor
		Board(const Board & cpy); // copy constructor
		virtual ~Board(); // destructor


		// helper; return vector of pieces given player colour
		std::vector<Piece*> & pieces(const std::string & colour) {return ((colour == "white") ? white : black);}	
		// helper; return king given player colour	
		Piece * king(const std::string & colour) {return ((colour == "white") ? white_king : black_king);}
		
		void Update_move(int x, int y, int x2, int y2); // move a piece
		void Update_select(int x, int y, int index, const std::string & type); // update a selected piece
	
		Square & square(int x, int y) {return grid[x][y];} // get square on board

		void Get_moves(Piece * p, std::vector<Square*> & v); // get allowed moves for piece

		// determine if position is on the board
		bool Valid_position(int x, int y) {return (x >= 0 && x <= BOARD_WIDTH-1 && y >= 0 && y <= BOARD_HEIGHT-1);}

	private:
		Square grid[BOARD_WIDTH][BOARD_HEIGHT];

	
		std::vector<Piece*> white;
		std::vector<Piece*> black;
		Piece * white_king;
		Piece * black_king;

		// Add a move to the vector if it is valid
		void Move(Piece * p, int x, int y, std::vector<Square*> & v);

		// Add all valid moves in a direction, stopping at the first invalid move
		void Scan(Piece * p, int vx, int vy, std::vector<Square*> & v);
};

#endif //_QCHESS_H

//EOF
