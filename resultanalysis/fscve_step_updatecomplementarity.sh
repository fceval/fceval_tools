#!/usr/bin/env bash

set -e
echo start_time:$(date +"%Y-%m-%d %H:%M:%S")
./fscve_step5_edge_coverage_analysis_repeated.sh
python fscve_step6_metric3_edge_coverage_complementarity.py
echo end_time:$(date +"%Y-%m-%d %H:%M:%S")


