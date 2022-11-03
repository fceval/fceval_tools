import pandas as pd

# calculate tables of edge coverage
benchmark = "nm"
expids = 20  # repeated times
benchmarks = {"cflow", "jq", "mp42aac", "nm", "objdump", "readelf", "libpng", "libxml2", "openssl", "lua"}  # "exiv2",
fcs = {"fca", "fcb"}
# calc the final results of unique bugs for repeated experiments
# out csv tables
dfs = []
for bm in benchmarks:
    df = pd.read_csv(f"csv/fscve_crash_analysis_bugcnt_unique_{bm}.csv").sort_values(
        by=["benchmark", "fuzzer_combination"], ascending=[True, False])
    # print(df)
    dfs.append(df)
df_unique_crashes_all = pd.concat(dfs, ignore_index=True).sort_values(by=["benchmark", "fuzzer_combination"],
                                                                      ascending=[True, False]).reset_index(drop=True)
# df_sanitizer_all["times"] = df_sanitizer_all["unique_bugcnt"]/df_sanitizer_all["avg"]
df_unique_crashes_all["times"] = df_unique_crashes_all.apply(lambda x: -1 if x["avg"] < 0.01 else x["unique_bugcnt"]/x["avg"], axis=1)
df_unique_crashes_all.drop(["Unnamed: 0"], axis=1, inplace=True)
print(df_unique_crashes_all)

df_unique_crashes_all.to_csv(f"csv/fscve_step7_metric2_unique_bugs.csv")

df_unique_crashes_all_transfer = df_unique_crashes_all.T
print(df_unique_crashes_all_transfer)
df_unique_crashes_all_transfer.to_csv(f"csv/fscve_step7_metric2_unique_bugs_transfer.csv")

# calc the final results of bugs detected by different sanitizers for repeated experiments
# out csv tables
dfs_sanitizer = []
for bm in benchmarks:
    df_sanitizer = pd.read_csv(f"csv/fscve_crash_analysis_step7_metric2_sanitizer_{bm}.csv").sort_values(
        by=["fuzzer_combination", "sanitizer", "crash_frames_hash"], ascending=[True, True, True])
    # print(df)
    dfs_sanitizer.append(df_sanitizer)
df_sanitizer_all = pd.concat(dfs_sanitizer, ignore_index=True).sort_values(by=["benchmark", "fuzzer_combination", "sanitizer", "crash_frames_hash"],
                                                                           ascending=[True, True, True, True]).reset_index(drop=True)

df_sanitizer_all.drop(["Unnamed: 0"], axis=1, inplace=True)
print(df_sanitizer_all)
df_sanitizer_all.to_csv(f"csv/fscve_step7_metric2_bugs_sanitizer.csv")

df_sanitizer_all_transfer = df_sanitizer_all.T
print(df_sanitizer_all_transfer)
df_sanitizer_all_transfer.to_csv(f"csv/fscve_step7_metric2_bugs_sanitizer_transfer.csv")
