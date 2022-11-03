#!/usr/bin/env bash

set -e
#cd /home/kakaxdu/collabfuzzzxy
#source venvnew/bin/activate

#fuzzers=("afl" "aflplusplus" "aflfast" "fairfuzz" "qsym" "radamsa" "honggfuzz" "libfuzzer" "angora" "parmesan" "symcc")
policies=("enfuzz" "casefc")
bms=("cflow" "jq" "mp42aac" "nm" "objdump" "readelf" "libpng"  "libxml2" "openssl" "lua")
fcs=("fca" "fcb")
expids=(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20)
finished=0
for fc in "${fcs[@]}"
do
	for expid in "${expids[@]}"
	do
		for bm in "${bms[@]}"
		do
			python fscve_step4_crash_analysis.py --bm "$bm" --fc "$fc" --expid "$expid"
		done

	done
done


