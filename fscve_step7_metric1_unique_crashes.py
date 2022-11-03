import pandas as pd

# calculate tables of edge coverage
benchmark = "nm"
expids = 10  # repeated times
benchmarks = {"cflow", "jq", "mp42aac", "nm", "objdump", "readelf", "libpng", "libxml2", "openssl", "lua"}  # "exiv2",
fcs = {"fca", "fcb"}
# calc the final results of unique crashes for repeated experiments
# out csv tables
dfs = []
for bm in benchmarks:
    df = pd.read_csv(f"csv/fscve_unique_crashes_results_repeated_{bm}.csv").sort_values(
        by=["fuzzer_combination", "fuzzer_combination"], ascending=[True, False])
    dfs.append(df)
df_unique_crashes_all = pd.concat(dfs, ignore_index=True).sort_values(by=["benchmark", "fuzzer_combination"],
                                                                      ascending=[True, False]).reset_index(drop=True)
df_unique_crashes_all.drop(["Unnamed: 0"], axis=1, inplace=True)
print(df_unique_crashes_all)

df_unique_crashes_all.to_csv(f"csv/fscve_step7_metric1_unique_crashes.csv")
df_unique_crashes_all_transfer = df_unique_crashes_all.T
print(df_unique_crashes_all_transfer)
df_unique_crashes_all_transfer.to_csv(f"csv/fscve_step7_metric1_unique_crashes_transfer.csv")

# aggregate the total unique crashes on all the benchmarks
# f"csv/fscve_crash_step7metric1_totalunique_{benchmark}.csv"
dfs_totalunique = []
for bm in benchmarks:
    df_totalunique = pd.read_csv(f"csv/fscve_crash_step7metric1_totalunique_{bm}.csv").sort_values(
        by=["fuzzer_combination", "fuzzer_combination"], ascending=[True, False])
    dfs_totalunique.append(df_totalunique)
df_totalunique_all = pd.concat(dfs_totalunique, ignore_index=True).sort_values(by=["benchmark", "fuzzer_combination"],
                                                                               ascending=[True, False]).reset_index(
    drop=True)
df_totalunique_all.drop(["Unnamed: 0"], axis=1, inplace=True)
print(df_totalunique_all)
df_totalunique_all.to_csv(f"csv/fscve_step7_metric1_totalunique_crashes.csv")
