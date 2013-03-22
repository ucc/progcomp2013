#ifndef _SILVERFISH_H
#define _SILVERFISH_H

#include "agent.h"

class Silver : public Agent
{
	public:
		Silver(const std::string & colour);
		Silver(const std::string & colour, const std::map<Piece::Type, double> & new_values);
		virtual ~Silver() {}
		
		virtual Square & Select();
		virtual Square & Move();

		std::map<Piece::Type, double> values;
};


#endif //_SILVERFISH_H