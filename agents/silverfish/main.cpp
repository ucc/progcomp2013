/**
 * silverfish : A Sample agent for UCC::Progcomp2013
 * @file main.cpp
 * @purpose The main function 
 */
#include <cstdlib>
#include <cstdio>
#include <iostream>

#include "silverfish.h"

using namespace std;

/**
 * @funct main
 * @purpose The main function; starts the agent
 * @param argc - Number of arguments, unused
 * @param argv - Argument string array, unused
 */
int main(int argc, char ** argv)
{
	srand(time(NULL)); // seed random number generator

	string colour; cin >> colour; // first read the colour of the agent

	try
	{
		Silver agent(colour); // create an agent using the colour
		agent.Run(cin, cout); // run the agent (it will read from cin and output to cout)
	}
	catch (const Exception & e)
	{
		return 1;
	}
	
	
	return 0; // Don't use exit(3), because it causes memory leaks in the C++ stdlib
}
