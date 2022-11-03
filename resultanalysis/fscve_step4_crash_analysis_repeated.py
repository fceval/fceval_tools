import pandas as pd

# calculate tables of crash uniques
# benchmark = "nm"
expids = 20
# fc = "fcb"
benchmarks = {"cflow", "jq", "mp42aac", "nm", "objdump", "readelf", "libpng", "libxml2", "openssl", "lua"}  # "exiv2",
fcs = {"fca", "fcb"}
for benchmark in benchmarks:
    #     for fc in fcs:
    #         dfs = []
    #         for expid in range(0, expids):
    #             df = pd.read_csv(f"csv/fscve_unique_crashes_{benchmark}_{fc}_{expid + 1}.csv")
    #             dfs.append(df)
    #         df_unique_crashes_all = pd.concat(dfs, ignore_index=True)
    #         cols_to_keep = ["benchmark", "fuzzer_combination", "experiment_id", "count"]
    #         df_unique_crashes_all.drop(df_unique_crashes_all.columns.difference(cols_to_keep), axis=1, inplace=True)
    #         print(df_unique_crashes_all)
    #         path_unique_crashes_all_csv = f"csv/fscve_unique_crashes_{benchmark}_{fc}_all.csv"
    #         df_unique_crashes_all.to_csv(path_unique_crashes_all_csv)
    #
    #     dfres = pd.DataFrame()
    #     df = pd.DataFrame()
    #     cols_to_keep = ["benchmark", "fuzzer_combination"]
    #     df_results = []
    #     # calc all data of a fuzzer combination on one benchmark
    #     for fc in fcs:
    #         for expid in range(0, expids):
    #             df = pd.read_csv(f"csv/fscve_unique_crashes_{benchmark}_{fc}_{expid + 1}.csv")
    #             df[f"experiment_id_{expid + 1}"] = df.loc[0, "count"]
    #             cols_to_keep.append(f"experiment_id_{expid + 1}")
    #             # print(df)
    #             dfres.drop(dfres.columns.difference(cols_to_keep), axis=1, inplace=True)
    #             if expid > 0:
    #                 dfres = pd.merge(dfres, df, on=["benchmark", "fuzzer_combination"])
    #             else:
    #                 dfres = df
    #         dfres.drop(dfres.columns.difference(cols_to_keep), axis=1, inplace=True)
    #         path_unique_crashes_result_csv = f"csv/fscve_unique_crashes_results_{benchmark}_{fc}.csv"
    #         dfres.to_csv(path_unique_crashes_result_csv)
    #         # print(dfres)
    #         df_results.append(dfres)
    #
    #     # merge two fuzzer combination
    #     df_result_final = pd.concat(df_results)
    #     cols_to_keep.remove("benchmark")
    #     cols_to_keep.remove("fuzzer_combination")
    #
    #     # dron non-digit columns for calculating
    #     df_result_drop = df_result_final.drop(dfres.columns.difference(cols_to_keep), axis=1)
    #     # print(df_result_final)
    #     # print("*"*30)
    #     # print(df_result_drop)
    #     # print("-"*30)
    #     df_result_final["max"] = df_result_drop.max(axis=1)
    #     df_result_final["avg"] = df_result_drop.mean(axis=1)
    #     #    df_result_final["avg"] = df_result_final["avg"].map(lambda x: int(x))  # float to int
    #     print(df_result_final)
    #     path_unique_crashes_result_final_csv = f"csv/fscve_unique_crashes_results_repeated_{benchmark}.csv"
    #     df_result_final.to_csv(path_unique_crashes_result_final_csv)

    # calc for unique real bugs
    for fc in fcs:
        dfs = []
        for expid in range(0, expids):
            df = pd.read_csv(f"csv/fscve_crash_analysis_bugcnt_{benchmark}_{fc}_{expid + 1}.csv")
            dfs.append(df)
        df_bugcnt_all = pd.concat(dfs, ignore_index=True)
        cols_to_keep = ["benchmark", "fuzzer_combination", "experiment_id", "bug_count"]
        df_bugcnt_all.drop(df_bugcnt_all.columns.difference(cols_to_keep), axis=1, inplace=True)
        print(df_bugcnt_all)
        path_bugcnt_all_csv = f"csv/fscve_crash_analysis_bugcnt_{benchmark}_{fc}_all.csv"
        df_bugcnt_all.to_csv(path_bugcnt_all_csv)

    # aggregate the bugcount data of repeated experiments ,the bugs are surely not unique ,only to represent the ability of a fuzzer combination on a benchmark during all the repeated times
    df = pd.DataFrame()
    dfres = pd.DataFrame()
    cols_to_keep = ["benchmark", "fuzzer_combination"]
    df_results = []
    # calc all data of a fuzzer combination on one benchmark
    for fc in fcs:
        for expid in range(0, expids):
            df = pd.read_csv(f"csv/fscve_crash_analysis_bugcnt_{benchmark}_{fc}_{expid + 1}.csv")
            df[f"experiment_id_{expid + 1}"] = df.loc[0, "bug_count"]
            cols_to_keep.append(f"experiment_id_{expid + 1}")
            # print(df)
            dfres.drop(dfres.columns.difference(cols_to_keep), axis=1, inplace=True)
            if expid > 0:
                dfres = pd.merge(dfres, df, on=["benchmark", "fuzzer_combination"])
            else:
                dfres = df
        dfres.drop(dfres.columns.difference(cols_to_keep), axis=1, inplace=True)
        dfres.to_csv(f"csv/fscve_crash_analysis_bugcnt_{benchmark}_{fc}.csv")
        # print(dfres)
        df_results.append(dfres)

    # merge two fuzzer combination
    df_result_final_bugcnt = pd.concat(df_results)
    cols_to_keep.remove("benchmark")
    cols_to_keep.remove("fuzzer_combination")
    print(cols_to_keep)
    print("*" * 20)
    print()
    # dron non-digit columns for calculating
    df_result_drop = df_result_final_bugcnt.drop(dfres.columns.difference(cols_to_keep), axis=1)
    # print(df_result_final)
    # print("*"*30)
    # print(df_result_drop)
    # print("-"*30)
    df_result_final_bugcnt["max"] = df_result_drop.max(axis=1)
    df_result_final_bugcnt["avg"] = df_result_drop.mean(axis=1)
    # df_result_final_bugcnt["avg"] = df_result_final_bugcnt["avg"].map(lambda x: int(x))  # float to int
    print(df_result_final_bugcnt)
    df_result_final_bugcnt.to_csv(f"csv/fscve_crash_analysis_bugcnt_repeated_{benchmark}.csv")

    # calc for unique real bug ,the time of bug find first , and calc the total number of unique real bugs of a fuzzer combination on one benchmark during all the repeated times
    df = pd.DataFrame()
    dfres = pd.DataFrame()
    cols_to_keep = ["discovery_time", "crash_frames_hash"]
    df_results = []
    # calc all data of a fuzzer combination on one benchmark
    dict_unique_bugcnt = []  # unique bug count of one fuzzer combination
    for fc in fcs:
        dfs = []
        for expid in range(0, expids):
            df = pd.read_csv(f"csv/fscve_crash_analysis_bugfindfirsttime_{benchmark}_{fc}_{expid + 1}.csv")
            df.drop(df.columns.difference(cols_to_keep), axis=1, inplace=True)
            dfs.append(df)
        dfres = pd.concat(dfs, ignore_index=True)
        dfres = dfres.drop_duplicates(['crash_frames_hash'])  # record once for special fuzzer and real bug
        dfres.to_csv(f"csv/fscve_crash_analysis_bugfindfirsttime_{benchmark}_{fc}.csv")
        dict_unique_bugcnt.append(dfres.shape[0])

        dfres["fuzzer_combination"] = [f"{fc}" for i in range(0, dfres.shape[0])]
        print(dfres)
        df_results.append(dfres)

    # calc the total number of unique real bugs of a fuzzer combination on one benchmark during all the repeated times
    df_result_final_bugcnt["unique_bugcnt"] = dict_unique_bugcnt
    # print(df_result_final_bugcnt)
    df_result_final_bugcnt.to_csv(f"csv/fscve_crash_analysis_bugcnt_unique_{benchmark}.csv")

    # merge two fuzzer combination to decide which fuzzer combination finds the same special bug faster
    df_result_final_bugfindfirsttime = pd.concat(df_results)
    df_result_same_bugs =df_result_final_bugfindfirsttime[df_result_final_bugfindfirsttime.duplicated('crash_frames_hash', keep=False)]
    df_result_same_bugs.to_csv(f"csv/fscve_step7_metric3_samebug_{benchmark}.csv")

    #keep the same bugs --> sort by bug and time --->  drop duplicate ---> sort by time
    # [df_result_final_bugfindfirsttime.duplicated('crash_frames_hash', keep=False)]
    df_result_final_bugfindfirsttime = df_result_final_bugfindfirsttime.sort_values(['crash_frames_hash',"discovery_time"]).drop_duplicates(['crash_frames_hash']).sort_values(["discovery_time"]).reset_index(drop=True)
    print(df_result_final_bugfindfirsttime)
    df_result_final_bugfindfirsttime.to_csv(f"csv/fscve_crash_analysis_bugdetail_findfirst_{benchmark}.csv")

    # add column
    df_result_final_bugfindfirsttime["bugcnt_findfirst"] = df_result_final_bugfindfirsttime["fuzzer_combination"]
    df_result_final_bugfindfirsttime = df_result_final_bugfindfirsttime.groupby("fuzzer_combination")[
        ["bugcnt_findfirst"]].count().reset_index(drop=False)
    df_result_final_bugfindfirsttime.to_csv(f"csv/fscve_crash_analysis_bugcnt_findfirst_{benchmark}.csv")
    print(df_result_final_bugfindfirsttime)

    # # calc total unique crashes of a fuzzer combination on a benchmark
    # dfres = pd.DataFrame()
    # df = pd.DataFrame()
    # cols_to_keep = ["benchmark", "fuzzer_combination", "testcase_hash"]
    # df_results = []
    # # calc all data of a fuzzer combination on one benchmark
    # for fc in fcs:
    #     dfs = []
    #     for expid in range(0, expids):
    #         df = pd.read_csv(f"csv/fscve_unique_crashes_step7metric1_{benchmark}_{fc}_{expid + 1}.csv")
    #         dfs.append(df)
    #     dfres = pd.concat(dfs, ignore_index=True)
    #     dfres.drop(dfres.columns.difference(cols_to_keep), axis=1, inplace=True)
    #     # print(dfres)
    #     # print(dfres.shape[1])
    #     dfres = dfres.drop_duplicates(["testcase_hash"])
    #     # print(dfres.shape[1])
    #     dfres.to_csv(f"csv/fscve_unique_crashes_step7metric1_{benchmark}_{fc}.csv")
    #     # print(dfres)
    #     df_results.append(dfres)
    #
    # # merge two fuzzer combination
    # df_result_benchmark = pd.concat(df_results, ignore_index=True)
    # df_result_drop = df_result_benchmark.drop(dfres.columns.difference(cols_to_keep), axis=1)
    # # print("*" * 30)
    # # print(df_result_drop)
    # # print("-" * 30)
    #
    # df_unique_crashes_total_count = df_result_drop.groupby(["benchmark", "fuzzer_combination"])[
    #     ["testcase_hash"]].count().reset_index(drop=False)
    # # print(df_unique_crashes_total_count)
    # # print(df_unique_crashes_total_count["testcase_hash"])
    # # add column
    # df_result_final_crash_step7metric1 = pd.DataFrame()
    # df_result_final_crash_step7metric1["benchmark"] = \
    #     df_result_drop.drop_duplicates(["benchmark", "fuzzer_combination"])["benchmark"]
    # df_result_final_crash_step7metric1["fuzzer_combination"] = \
    #     df_result_drop.drop_duplicates(["benchmark", "fuzzer_combination"])["fuzzer_combination"]
    # df_result_final_crash_step7metric1["total_unique"] = df_unique_crashes_total_count["testcase_hash"].to_list()
    # df_result_final_crash_step7metric1 = df_result_final_crash_step7metric1.reset_index(drop=True)
    # df_result_final_crash_step7metric1.to_csv(f"csv/fscve_crash_step7metric1_totalunique_{benchmark}.csv")
    # print(df_result_final_crash_step7metric1)

    # calc which fuzzer combination finds which bug using which sanitizer
    dfres_sanitizer = pd.DataFrame()
    df_sanitizer = pd.DataFrame()
    cols_to_keep_sanitizer = ["benchmark", "fuzzer_combination", "sanitizer", "crash_frames_hash", "crash_id"]
    df_results_sanitizer = []
    # calc all data of a fuzzer combination on one benchmark
    for fc in fcs:
        dfs_sanitizer = []
        for expid in range(0, expids):
            df_sanitizer = pd.read_csv(
                f"csv/fscve_crash_analysis_step7_metric2_sanitizer_{benchmark}_{fc}_{expid + 1}.csv")
            dfs_sanitizer.append(df_sanitizer)
        dfres_sanitizer = pd.concat(dfs_sanitizer, ignore_index=True)
        # dfres_sanitizer.drop(dfres.columns.difference(cols_to_keep_sanitizer), axis=1, inplace=True)
        # print(dfres_sanitizer)
        # print(dfres_sanitizer.shape[1])
        # print(dfres_sanitizer.shape[1])
        dfres_sanitizer.to_csv(f"csv/fscve_crash_analysis_step7_metric2_sanitizer_{benchmark}_{fc}.csv")
        # print(dfres_sanitizer)
        df_results_sanitizer.append(dfres_sanitizer)

    # merge two fuzzer combination
    df_result_benchmark_sanitizer = pd.concat(df_results_sanitizer, ignore_index=True)
    df_result_drop_sanitizer = df_result_benchmark_sanitizer.drop(
        dfres_sanitizer.columns.difference(cols_to_keep_sanitizer),
        axis=1).sort_values(by=["fuzzer_combination", "sanitizer", "crash_frames_hash"], ascending=[True, True, True])
    df_result_drop_sanitizer = df_result_drop_sanitizer.drop_duplicates(["fuzzer_combination", "sanitizer", "crash_frames_hash"]).reset_index(drop=True)
    # print("*" * 30)
    # print(df_result_drop_sanitizer)
    # print("-" * 30)
    df_result_drop_sanitizer.to_csv(f"csv/fscve_crash_analysis_step7_metric2_sanitizer_{benchmark}.csv")

print("************finished:fscve_step4_crash_analysis_repeated*********************")
