#!/bin/bash

# This script can be used to remove all results
# For testing purposes

. vars

rm -f web/current.log

rm -rf $results_dir

for s in *.result; do
	rm -f $s
done

cd $agent_dir
for s in $(find . | grep score.dat); do
	rm -f $s
done
		


