#!/usr/bin/env bash

set -e
#cd /home/kakaxdu/collabfuzzzxy
#source venvnew/bin/activate

bms=("cflow" "jq" "mp42aac" "nm" "objdump" "readelf" "libpng"  "libxml2" "openssl" "lua")
times=20

for bm in "${bms[@]}"
do
  python fscve_step5_edge_coverage_analysis_repeated.py --bm "$bm" --times "$times"
done



