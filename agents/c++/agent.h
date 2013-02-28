/**
 * agent++ : A Sample agent for UCC::Progcomp2013
 * @file agent.h
 * @purpose Declaration of Agent class
 */

#ifndef _AGENT_H
#define _AGENT_H

#include <iostream>
#include <sstream>
#include "qchess.h" // Declarations of Board, Piece and Square classes; see also qchess.cpp

/**
 * @class Agent
 * @purpose Class that represents an agent which will play qchess
 */
class Agent
{
	public:
		Agent(const std::string & colour); // initialise with colour
		virtual ~Agent(); // destructor

		void Run(std::istream & in, std::ostream & out); // agent run loop, specify input and output streams
		
		virtual Square & Select(); // select a square (default: random square containing one of my pieces)
		virtual Square & Move(); // select a move (default: random valid move for selected piece)

	
	protected:
		const Piece::Colour colour; // colour of the agent; do not change it
		Board board; // board, see qchess.h
		Piece * selected; // last piece chosen by Agent::Select, see qchess.h
		
};

#endif //_AGENT_H

//EOF
