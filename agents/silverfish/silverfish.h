#ifndef _SILVERFISH_H
#define _SILVERFISH_H

#include "agent.h"

class Silver : public Agent
{
	public:
		Silver(const std::string & colour, int max_depth=2;);
		Silver(const std::string & colour, const std::map<Piece::Type, double> & new_values, int max_depth=2;);
		virtual ~Silver() {}
		
		virtual Square & Select();
		virtual Square & Move();
		
		std::map<Piece::Type, double> values;
		int max_depth;
		int depth;
		
};

class Move
{
	public:
		Move(Piece * new_p, Square & new_s, double new_score) : p(new_p), s(new_s), score(new_score) {}
		virtual ~Move() {}
		Move(const Move & cpy) : p(cpy.p), s(cpy.s), score(cpy.score) {}
		
		Piece * p;
		Square & s;
		double score;
		
		bool operator>(const Move & m) const {return score > m.score;}
		bool operator<(const Move & m) const {return score < m.score;}
};


#endif //_SILVERFISH_H