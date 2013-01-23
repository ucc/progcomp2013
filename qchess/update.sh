#!/bin/bash

# I still can't believe I am doing this

target=qchess.py
components="piece.py board.py player.py thread_util.py game.py graphics.py main.py"
# The below seems nicer, but doesn't work because things need to be imported in the right order :(
#components=$(ls *.py | tr '\t' '\n' | grep -v $target)

header="#!/usr/bin/python -u"
footer="# EOF - created from update.sh on $(date)"



# If the target was modified more recently than any of the components, update the component file
target_mod=$(stat -c %Y $target)

merge_required=false

for f in $components; do
	if [ $(stat -c %Y $f) -lt $target_mod ]; then
		nawk "/+++ $f +++/, /--- $f ---/" $target | grep -v "+++ $f +++" | grep -v "\--- $f ---" > $f
	else
		merge_required=true
done

if $merge_required; then
	echo $header > $target
	for f in $components; do
		cat $components >> $target
	done

	echo $footer > $target
fi
