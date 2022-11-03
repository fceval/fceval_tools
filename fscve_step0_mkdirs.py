import os
import shutil

from pyutilszxy import makedirs
print("fscve make dirs start..........")
benchmarks = {"cflow", "exiv2", "jq", "mp42aac"}
repeated_times = 5
# for bm in benchmarks:
#     for exid in range(repeated_times):
#         makedirs(f"runinfosqlites/{bm}/fca/{exid + 1}", mode=0o777, ignore_errors=False, exist_ok=True)
#         makedirs(f"runinfosqlites/{bm}/fcb/{exid + 1}", mode=0o777, ignore_errors=False, exist_ok=True)

shutil.rmtree("csv", ignore_errors=True)
shutil.rmtree("image", ignore_errors=True)

makedirs("csv", mode=0o777, ignore_errors=False, exist_ok=True)
# makedirs("csv/fscve_step2_crashrunner", mode=0o777, ignore_errors=False, exist_ok=True)
# makedirs("csv/fscve_step4_crash_analysis", mode=0o777, ignore_errors=False, exist_ok=True)
# makedirs("csv/fscve_step4_crash_analysis_repeated", mode=0o777, ignore_errors=False, exist_ok=True)
# makedirs("csv/fscve_step5_edge_coverage_analysis", mode=0o777, ignore_errors=False, exist_ok=True)
# makedirs("csv/fscve_step5_edge_coverage_analysis_repeated", mode=0o777, ignore_errors=False, exist_ok=True)
makedirs("image", mode=0o777, ignore_errors=False, exist_ok=True)
# makedirs("image/fscve_step2_crashrunner", mode=0o777, ignore_errors=False, exist_ok=True)
# makedirs("image/fscve_step4_crash_analysis", mode=0o777, ignore_errors=False, exist_ok=True)
# makedirs("image/fscve_step4_crash_analysis_repeated", mode=0o777, ignore_errors=False, exist_ok=True)
# makedirs("image/fscve_step5_edge_coverage_analysis", mode=0o777, ignore_errors=False, exist_ok=True)
# makedirs("image/fscve_step5_edge_coverage_analysis_repeated", mode=0o777, ignore_errors=False, exist_ok=True)

print("fscve make dirs end")
