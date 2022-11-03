import pandas as pd

# calculate tables of edge coverage
benchmark = "nm"
expids = 20  # repeated times
benchmarks = {"cflow", "jq", "mp42aac", "nm", "objdump", "readelf", "libpng", "libxml2", "openssl", "lua"}  # "exiv2",
fcs = {"fca", "fcb"}
# calc the final results of the number of first found unique bugs for repeated experiments
# out csv tables
#clac the average nubmer of unique bugs discovered by one fc over time in 20 repeated experiments
for bm in benchmarks:
    for fc in fcs:
        dfs = []
        for expid in range(1,expids+1):
            df_wftcbug_venn = pd.read_csv(f"csv/fscve_crash_analysis_{bm}_{fc}_{expid}.csv")
            # df_wftcbug_venn.set_index(df_wftcbug_venn["crash_id"], inplace=True)
            find_bug_first_cols_to_keep = ["discovery_id", "discovery_time", "crash_frames_hash",]
            df_bug_speed = df_wftcbug_venn.drop_duplicates(['crash_frames_hash'], keep="first", ignore_index=True )  # record once for special fuzzer and real bug
            df_bug_speed = df_bug_speed.drop(df_bug_speed.columns.difference(find_bug_first_cols_to_keep), axis=1)
            df_bug_speed["discovery_time"] =  df_bug_speed["discovery_time"] // 60  # minutes
            # print(df_bug_speed)
            # print("**"*20)
            dfs.append(df_bug_speed)
        df_bug_speed_bm = pd.concat(dfs, ignore_index=True).sort_values(
            by=["discovery_time"],ignore_index=True)
        df_bug_speed_bm["count"]=(df_bug_speed_bm.index+1)/expids
        df_bug_speed_bm.to_csv(f"csv/fscve_step7_metric3_speed_average_{bm}_{fc}.csv")
        print(df_bug_speed_bm)
        print(f"**-{bm}_{fc}-**"*20)
