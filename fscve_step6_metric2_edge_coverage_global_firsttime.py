import pandas as pd

# calculate tables of edge coverage
benchmark = "nm"
expids = 20  # repeated times
benchmarks = {"cflow", "jq", "mp42aac", "nm", "objdump", "readelf", "libpng", "libxml2", "openssl", "lua"}  # "exiv2",
fcs = {"fca", "fcb"}
# calc the final results of when the smaller of the two fuzzers'  max global edge coverage
# on the benchmarks was achieved for repeated experiments
# out csv tables
dfs = []
for bm in benchmarks:
    df = pd.read_csv(f"csv/fscve_edge_global_results_firsttime_{bm}.csv").sort_values(by=["fuzzer_combination"],
                                                                                      ascending=[False])
    # print(df)
    dfs.append(df)
df_edge_count_global_all = pd.concat(dfs, ignore_index=True).sort_values(by=["benchmark", "fuzzer_combination"],
                                                                         ascending=[True, False]).reset_index(drop=True)
df_edge_count_global_all.drop(["Unnamed: 0"], axis=1, inplace=True)
print(df_edge_count_global_all)
df_edge_count_global_all.to_csv(f"csv/fscve_step6_metric2_edge_coverage_global_firsttime_all.csv")
