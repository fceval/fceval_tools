#!/usr/bin/env bash

set -e
echo start_time:$(date +"%Y-%m-%d %H:%M:%S")
#./fscve_step0_pre_data_within24h.sh
#python fscve_step0_mkdirs.py
#./fscve_step2_crashrunner.sh
#./fscve_step4_crash_analysis.sh
python fscve_step4_crash_analysis_repeated.py
./fscve_step5_edge_coverage_analysis.sh
./fscve_step5_edge_coverage_analysis_repeated.sh
python fscve_step6_metric1_edge_coverage_global.py
python fscve_step6_metric2_edge_coverage_global_firsttime.py
python fscve_step6_metric3_edge_coverage_complementarity.py
python fscve_step6_metric2_edge_coverage_a12score.py
#python fscve_step7_metric1_unique_crashes.py
python fscve_step7_metric2_unique_bugs.py
python fscve_step7_metric3_unique_bugs_firsttime.py
python fscve_step7_metric2_unique_bugs_a12score.py
python fscve_step7_metric3_unique_bugs_speed.py
echo end_time:$(date +"%Y-%m-%d %H:%M:%S")


