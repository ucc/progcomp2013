#!/bin/bash

# This script runs a single round of the competition

. vars

agents=""



# Copy messages to a log file
if [ "$BASH_ARGV" != "_worker_" ]; then
	# Get the round number
	mkdir -p $results_dir
	cd $results_dir
	round=$(ls | grep "round" | sed -e "s:round::g" | sort -n | head --lines=1)
	if [ "$round" == "" ]; then round=0; fi
	round=$(( $round + 1 ))
	mkdir -p round$round
	cd $root_dir
	exec $0 "$@" _worker_ 2>&1 | tee $results_dir/round$round/run.log
	exit $?
else
	cd $results_dir
	round=$(ls | grep "round" | sed -e "s:round::g" | sort -n | head --lines=1)
fi

echo "Start at $(date)"

# Setup the swarm
if [ "$swarm_hosts" != "" ]; then
	swarm --daemon
	for h in $swarm_hosts; do
		swarm -c "#ABSORB $h#"
	done
	swarm -c "#.*# cd $root_dir; mkdir -p $results_dir/round$round"
fi



cd $root_dir/$agent_dir
count=0
for f in $(ls); do
	if [ -d $f ]; then
		info_file=$(ls $f | grep -w "info")
		if [ "$info_file" == "" ]; then
			echo "Skipping agent $f (missing info file)"
		else
			count=$(( $count + 1 ))
			agents="$agents $f"
		fi
	fi
done
echo "Found $count agents in $agent_dir/"



# Add all the games to swarm
cd $root_dir

if [ "$agents" == "" ]; then
	echo "No agents to run round $round with" 1>&2
	rm -rf "$results_dir/round$round"
	exit 1
fi

echo "Start round $round"

game=0
for a in $agents; do
	runa="$agent_dir/$a/$(head --lines=1 $agent_dir/$a/info)"
	for b in $agents; do
		if [ "$a" == "$b" ]; then continue; fi
		for ((i=1;i<=$games_per_pair;++i)); do
			runb="$agent_dir/$b/$(head --lines=1 $agent_dir/$b/info)"
			f="${a}_${b}_${i}"

			game=$(( $game + 1))	
			l="$results_dir/round$round/$f.log"
			err="$results_dir/round$round/$f.err"

			echo "Game #$game: $a .vs. $b ($i of $games_per_pair)"
			if [ "$swarm_hosts" != "" ]; then
				swarm -c "$qchess --no-graphics \"$runa\" \"$runb\" --log=$l --log=@web/current.log 2>$err" -o $f.result
			else
				$qchess --no-graphics "$runa" "$runb" --log=$l --log=@web/current.log 1> $f.result 2> $err
				if [ "$(wc -l $err | awk '{print $1}')" == "0" ]; then rm $err; fi
			fi
		done
	done
done



if [ "$swarm_hosts" != "" ]; then
	swarm -c "#BARRIER BLOCK#" # Wait for all games to finish

	#Copy over log files (start before updating scores as the scp may take some time)
	for h in "local $swarm_hosts"; do
		cmd="
		if [ \"\$(hostname)\" != \"$webserver\" ]; then
			cd $root_dir/$results_dir/round$round;
			for i in *.log *.err; do
				if [ \"\$(wc -l \$i | awk '{print \$1}')\" != 0 ]; then
					scp \$i $webserver/$root_dir/$results_dir/round$round/\$i
				fi
			done
		fi"
		swarm -c "#$h:.* \$# $cmd" # Execute once on each host
	done
fi

echo "Completed $games games with $count agents"

# A bash function. Yes, they do exist.
function update_score
{
	if [ -e $agent_dir/$1/score.dat ]; then
		score=$(tail --lines=1 $agent_dir/$1/score.dat | awk '{print $1}')
	else
		score=0
	fi
	

	score=$(( $score + $3 ))
	echo "$3 $score $2 $4 $5" >> $agent_dir/$1/score.dat
	return $score
}

# Go through results
for f in *.result; do
	log=round$round/$(echo $f.log | sed -e "s:.result::g")
	white=$(echo $f | tr '_' '\t' | awk '{print $1}')
	black=$(echo $f | tr '_' '\t' | awk '{print $2}')
	if [ "$(cat $f)" == "white" ]; then
		update_score $white $black $win_score WIN $log
		update_score $black $white $loss_score LOSS $log
	elif [ "$(cat $f)" == "black" ]; then
		update_score $white $black $loss_score LOSS $log
		update_score $black $white $win_score WIN $log
	elif [ "$(cat $f)" == "DRAW" ]; then
		update_score $white $black $draw_score DRAW $log
		update_score $black $white $draw_score DRAW $log
	else
		echo "Unrecognised result \"$(cat $f)\" in $f" 1>&2
	fi

	rm $f
done

echo "Updated scores"

#Close the swarm
if [ "$swarm_hosts" != "" ]; then
	swarm -c "#BARRIER BLOCK#"
	swarm -c "#.*# exit"
fi

echo "Finished at $(date)"

