import pandas as pd

# calculate tables of edge coverage
benchmark = "nm"
expids = 20  # repeated times
benchmarks = {"cflow", "jq", "mp42aac", "nm", "objdump", "readelf", "libpng", "libxml2", "openssl", "lua"}  # "exiv2",
fcs = {"fca", "fcb"}
# calc the final results of the number of first found unique bugs for repeated experiments
# out csv tables
dfs = []
for bm in benchmarks:
    df = pd.read_csv(f"csv/fscve_crash_analysis_bugcnt_findfirst_{bm}.csv").sort_values(
        by=["fuzzer_combination", "fuzzer_combination"], ascending=[True, False])
    df["benchmark"] = [f"{bm}" for i in range(0, df.shape[0])]
    df.drop(["Unnamed: 0"], axis=1, inplace=True)
    # print(df)
    # print("*"*20)
    # for the fc which has found no bug earlier,the csv row is none
    # we should add  the row here
    df2 = pd.DataFrame([["fcb", 0, f"{bm}"], ["fca", 0, f"{bm}"]],
                       columns=["fuzzer_combination", "bugcnt_findfirst", "benchmark"])
    # print(df2)
    # print("@"*20)
    df = pd.concat([df, df2])
    # print(df)
    # print("&"*20)
    df = df.drop_duplicates(["benchmark", "fuzzer_combination"])
    # print(df)
    dfs.append(df)
df_bugcnt_findfirst_all = pd.concat(dfs, ignore_index=True).sort_values(by=["benchmark", "fuzzer_combination"],
                                                                        ascending=[True, False]).reset_index(drop=True)
df_bugcnt_findfirst_all = df_bugcnt_findfirst_all[["benchmark", "fuzzer_combination", "bugcnt_findfirst"]]
print(df_bugcnt_findfirst_all)
df_bugcnt_findfirst_all.to_csv(f"csv/fscve_step7_metric3_bugcnt_findfirst.csv")
