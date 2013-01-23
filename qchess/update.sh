#!/bin/bash

# I still can't believe I am doing this

# (This can't be done with gnu make, because of circular dependency issues)

target=qchess.py
components="piece.py board.py player.py thread_util.py game.py graphics.py main.py"
# The below seems nicer, but doesn't work because things need to be imported in the right order :(
#components=$(ls *.py | tr '\t' '\n' | grep -v $target)

header="#!/usr/bin/python -u"
footer="# EOF - created from update.sh on $(date)"



# If the target was modified more recently than any of the components, update the component file
target_mod=$(stat -c %Y $target 2>/dev/null)

if [ $? -ne 0 ]; then
	merge_required=true
else
	merge_required=false

	for f in $components; do
		
		component_mod=$(stat -c %Y $f 2>/dev/null)
		if [ $? -ne 0 ]; then
			update_required=true
		elif [ $component_mod -lt $target_mod ]; then
			update_required=true
		else
			update_required=false
		fi

		if $update_required; then
			echo "$0 - update $f from $target"
			sanity=$(egrep "(+++ $f +++)|(--- $f ---)" $target | wc -l)
			if [ $sanity -ne 2 ]; then
				$(echo "$0 - $target does not have markers for $f in it!") 1>&2
				exit 1
			fi
			cp $f $f~
			new_contents=$(nawk "/+++ $f +++/, /--- $f ---/" $target | grep -v "+++ $f +++" | grep -v "\--- $f ---")
			
			echo "$new_contents" > $f
		else
			echo "$0 - $f is newer than $target"
			merge_required=true
		fi
	done
fi

# If any components were modified more recently than the target, merge the components into the target
if $merge_required; then
	echo $header > $target
	for f in $components; do
		echo "$0 - merge $f into $target"
		echo "# +++ $f +++ #" >> $target
		cat $f >> $target
		echo "# --- $f --- #" >> $target
	done

	echo $footer >> $target
	chmod u+x $target
fi
