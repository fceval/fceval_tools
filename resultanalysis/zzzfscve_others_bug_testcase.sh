#!/usr/bin/env bash
set -e
bms=("cflow" "exiv2" "jq" "mp42aac")
fcs=("fca" "fcb")
expids=(1 2 3 4 5)
for fc in "${fcs[@]}"
do
	for expid in "${expids[@]}"
	do
		for bm in "${bms[@]}"
		do
		  python zzzfscve_others_bug_testcase.py --bm "$bm" --fc "$fc" --expid "$expid"
		done
	done
done


