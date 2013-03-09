#!/bin/bash

# Qchess login script
# Only works with GDM
# WARNING: Don't use on systems without GDM, because it will probably break everything
# Add to root's crontab to run every minute

# Check qchess isn't already running
if [ "$(ps aux | grep -v grep | grep "qchess\.py" | wc -l)" != "0" ]; then
	echo "qchess already running" 1>&2
	(ps aux | grep -v grep | grep qchess) 1>&2
	exit 0
fi

# Check that only GDM is running gnome-session
# This should indicate that the login selection is being shown
session_types="gnome-session\|kdeinit"
non_gdm_sessions=$(ps aux | grep -v grep | grep "$session_types" | awk '{print $1}' | grep -v gdm | wc -l)

if [ "$non_gdm_sessions" != 0 ]; then
	echo "$non_gdm_sessions non gdm sessions running" 1>&2
	exit 0
fi

# OK, go ahead and do evil stuff

export DISPLAY=:1
p=$(pwd)
cd /home/wheel/matches/progcomp2013/qchess
win="black"

#espeak "I challenge you to a duel!"
while [ "$win" == "black" ]; do
	win=$(./qchess.py @human @internal:AgentBishop)
done

#if [ "$win" == "white" ]; then
#	espeak "I'll beat you next time."
#else
#	espeak "You dirty, cheating, human."
#fi
cd $p
