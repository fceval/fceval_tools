import argparse

import pandas as pd
import re


def parse_args():
    parser = argparse.ArgumentParser(
        description="you should add those parameter benchmark--bm repeated_times--times  ")
    parser.add_argument('--bm', help="benchmark name")
    parser.add_argument('--times', help="repeated times of experiments")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    benchmark = args.bm
    print(type(args.times))
    expids = int(args.times)  # repeated times
    fcs = {"fca", "fcb"}
    print(f"{benchmark}----{expids}")

    # ********************************************************************
    # **********************************************************************
    # ***********************************************************************
    # alc the global edge coverage for repeaded experiments
    print(
        """
        # ********************************************************************
        # **********************************************************************
        # ***********************************************************************
        # #alc the global edge coverage for repeaded experiments
        """
    )

    for fc in fcs:
        dfs = []
        for expid in range(0, expids):
            df = pd.read_csv(f"csv/fscve_edge_count_global_{benchmark}_{fc}_{expid + 1}.csv")
            dfs.append(df)
        df_edge_count_global_all = pd.concat(dfs, ignore_index=True)
        cols_to_keep = ["benchmark", "fuzzer_combination", "experiment_id", "edge_count"]
        df_edge_count_global_all.drop(df_edge_count_global_all.columns.difference(cols_to_keep), axis=1, inplace=True)
        print(df_edge_count_global_all)
        df_edge_count_global_all.to_csv(f"csv/fscve_edge_count_global_{benchmark}_{fc}_all.csv")

    # ********************************************************************
    # **********************************************************************
    # ***********************************************************************
    # calc all data of a fuzzer combination on one benchmark
    print(
        """
        # ********************************************************************
        # **********************************************************************
        # ***********************************************************************
        # #calc all data of a fuzzer combination on one benchmark
        """
    )

    dfres = pd.DataFrame()
    df = pd.DataFrame()
    cols_to_keep = ["benchmark", "fuzzer_combination"]
    df_results = []
    # calc all data of a fuzzer combination on one benchmark
    for fc in fcs:
        for expid in range(0, expids):
            df = pd.read_csv(f"csv/fscve_edge_count_global_{benchmark}_{fc}_{expid + 1}.csv")
            df[f"experiment_id_{expid + 1}"] = df.loc[0, "edge_count"]
            cols_to_keep.append(f"experiment_id_{expid + 1}")
            # print(df)
            dfres.drop(dfres.columns.difference(cols_to_keep), axis=1, inplace=True)
            if expid > 0:
                dfres = pd.merge(dfres, df, on=["benchmark", "fuzzer_combination"])
            else:
                dfres = df
        dfres.drop(dfres.columns.difference(cols_to_keep), axis=1, inplace=True)
        path_unique_crashes_result_csv = f"csv/fscve_edge_count_global_results_{benchmark}_{fc}.csv"
        dfres.to_csv(path_unique_crashes_result_csv)
        # print(dfres)
        df_results.append(dfres)

    # merge two fuzzer combination
    df_result_final = pd.concat(df_results, ignore_index=True)
    cols_to_keep.remove("benchmark")
    cols_to_keep.remove("fuzzer_combination")

    # dron non-digit columns for calculating
    df_result_drop = df_result_final.drop(dfres.columns.difference(cols_to_keep), axis=1)
    # print(df_result_final)
    # print("*"*30)
    # print(df_result_drop)
    # print("-"*30)
    df_result_final["max"] = df_result_drop.max(axis=1)
    df_result_final["avg"] = df_result_drop.mean(axis=1)
    df_result_final["avg"] = df_result_final["avg"].map(lambda x: int(x))  # float to int
    print(df_result_final)
    df_result_final.to_csv(f"csv/fscve_edge_count_global_results_repeated_{benchmark}.csv")

    # ********************************************************************
    # **********************************************************************
    # ***********************************************************************
    # calc the time when max coverage(the smaller of the two fuzzer combinations) achieved
    print(
        """
        # ********************************************************************
        # **********************************************************************
        # ***********************************************************************
        #calc the time when max coverage(the smaller of the two fuzzer combinations) achieved
        """
    )

    dfres = pd.DataFrame()
    df = pd.DataFrame()
    dfs = []
    cols_to_keep = ["benchmark", "fuzzer_combination"]
    df_edge_global_first_time_fcs = []
    first_time_fcs = []
    fcs_results = []
    # calc all data of a fuzzer combination on one benchmark
    for fc in fcs:
        df_result_max_edge_count_global_fc = pd.read_csv(
            f"csv/fscve_edge_count_global_results_repeated_{benchmark}.csv")
        df_result_max_edge_count_global_fc.reset_index(drop=True)
        # print(df_result_max_edge_count_global_fc)
        max_edge_count_smaller = min(df_result_max_edge_count_global_fc.loc[0, "max"],
                                     df_result_max_edge_count_global_fc.loc[1, "max"])
        print(f"max_edge_count_smaller:{max_edge_count_smaller}")
        dfs = []
        for expid in range(0, expids):
            df = pd.read_csv(f"csv/fscve_edge_history_global_{benchmark}_{fc}_{expid + 1}.csv")
            dfs.append(df)
        df_edge_history_global_onefc = pd.concat(dfs, ignore_index=True).sort_values(by=["edges_count", "time"])
        # edge coverage global history of one fuzzer combinations
        # df_edge_history_global_onefc.to_csv(f"csv/fscve_edge_history_global_{benchmark}_{fc}.csv")
        # print(df_edge_history_global_onefc)

        # calc the time when max coverage(the smaller of the two fuzzer combinations) achieved by one fuzzer combination(fc)
        first_time_fc = \
            df_edge_history_global_onefc[df_edge_history_global_onefc['edges_count'] >= max_edge_count_smaller].head(
                1).iloc[
                0, 3]
        df_edge_global_first_time_fc = pd.DataFrame()
        df_edge_global_first_time_fc["benchmark"] = [benchmark]
        df_edge_global_first_time_fc["fuzzer_combination"] = [fc]
        df_edge_global_first_time_fc["max_coverage_global_smaller"] = [max_edge_count_smaller]
        df_edge_global_first_time_fc["first_time"] = [first_time_fc]
        df_edge_global_first_time_fc.to_csv(f"csv/fscve_edge_global_results_firsttime_{benchmark}_{fc}.csv")
        print(df_edge_global_first_time_fc)
        df_edge_global_first_time_fcs.append(df_edge_global_first_time_fc)

    # merge two fuzzer combination
    print("*result*" * 20)
    df_edge_global_first_time_result = pd.concat(df_edge_global_first_time_fcs, ignore_index=True)
    print(df_edge_global_first_time_result)
    df_edge_global_first_time_result.to_csv(f"csv/fscve_edge_global_results_firsttime_{benchmark}.csv")

    # ********************************************************************
    # **********************************************************************
    # ***********************************************************************
    # calc the global edge history of the repeated experiments on a special benchmark
    # for drawing history curve graph
    # draw the comparing graph of two fuzzer combinations on itself's 10 repeated times
    print(
        """
        # ********************************************************************
        # **********************************************************************
        # ***********************************************************************
        #calc the global edge history of the repeated experiments on a special benchmark
        #for drawing history curve graph
        #draw the comparing graph of two fuzzer combinations on itself's 10 repeated times
        """
    )
    # calc the global edge history of the repeated experiments on a special benchmark
    # for drawing history curve graph
    # draw the comparing graph of two fuzzer combinations on itself's 10 repeated times
    df = pd.DataFrame()
    dfs = []
    cols_to_keep_history_global = ["edges_count", "time", "experiment_id"]
    df_edge_global_first_time_fcs = []
    # calc all data of a fuzzer combination on one benchmark
    for fc in fcs:
        dfs = []
        for expid in range(0, expids):
            df = pd.read_csv(f"csv/fscve_edge_history_global_{benchmark}_{fc}_{expid + 1}.csv")
            df["experiment_id"] = [expid + 1 for i in range(0, df.shape[0])]
            dfs.append(df)
        df_edge_history_global_onefc = pd.concat(dfs, ignore_index=True).sort_values(
            by=["experiment_id", "edges_count", "time"])
        df_edge_history_global_onefc = df_edge_history_global_onefc.drop(
            df_edge_history_global_onefc.columns.difference(cols_to_keep_history_global), axis=1)
        # edge coverage global history of one fuzzer combinations
        df_edge_history_global_onefc.to_csv(f"csv/fscve_edge_history_global_{benchmark}_{fc}.csv")
        print(df_edge_history_global_onefc)

    # ********************************************************************
    # **********************************************************************
    # ***********************************************************************
    # complementary measurement
    # step1:search the edges that the two fuzzer combinations have found in common on a benchmark in all repeated experiments
    #      merge the results of repeated experiments of a fuzzer combination（fc）on  a benchmark, collect the times each edge has been found by one fuzzer

    # step2:for each fuzzer combination(fc) ,calc its complementary measurement,by the formulation:  sum(1-II(1-pi))
    print(
        """
        # ********************************************************************
        # **********************************************************************
        # ***********************************************************************
        # complementary measurement
        # step1:search the edges that the two fuzzer combinations have found in common on a benchmark in all repeated experiments
        #      merge the results of repeated experiments of a fuzzer combination（fc）on  a benchmark, collect the times each edge has been found by one fuzzer
        
        # step2:for each fuzzer combination(fc) ,calc its complementary measurement,by the formulation:  sum(1-II(1-pi))
        """
    )

    dfs_benchmark = []
    cols_to_keep_edge_detail = ["fuzzer", "edge"]
    # df_edge_detail_fcs = []
    df_edge_detail_fcs_no_dulicates = []
    dict_fc_dataframe_detail = {}
    dict_results_complemetary_measurement = {}
    dict_values_fc = []
    dict_values_complemetary_measurement = []
    # calc all data of a fuzzer combination on one benchmark
    for fc in fcs:
        dfs = []
        for expid in range(0, expids):
            df = pd.read_csv(f"csv/fscve_edge_detail_{benchmark}_{fc}_{expid + 1}.csv")
            df["edge"] = df["block_source"].astype("str") + df["block_target"].astype("str").map(lambda x: "-" + x)
            dfs.append(df)
            # print(df)
        df_edge_detail_onefc = pd.concat(dfs, ignore_index=True)
        df_edge_detail_onefc = df_edge_detail_onefc.drop(
            df_edge_detail_onefc.columns.difference(cols_to_keep_edge_detail), axis=1).sort_values(
            by=["edge", "fuzzer"])

        # edge coverage global history of one fuzzer combinations
        df_edge_detail_onefc.to_csv(f"csv/fscve_edge_detail_{benchmark}_{fc}.csv")
        # print(df_edge_detail_onefc)
        # df_edge_detail_fcs.append(df_edge_detail_onefc)
        dict_fc_dataframe_detail[fc] = df_edge_detail_onefc

        # delete duplicated edges for every fuzzer combination
        print("aaaaa", df_edge_detail_onefc.shape[0])
        df_edge_detail_onefc_no_duplicates = df_edge_detail_onefc.drop_duplicates(['edge'])
        print("bbbbbb", df_edge_detail_onefc_no_duplicates.shape[0])
        df_edge_detail_onefc_no_duplicates["fuzzer_combination"] = fc
        df_edge_detail_onefc_no_duplicates["benchmark"] = benchmark
        df_edge_detail_onefc_no_duplicates = df_edge_detail_onefc_no_duplicates.reset_index(drop=True)
        print(df_edge_detail_onefc_no_duplicates)
        df_edge_detail_fcs_no_dulicates.append(df_edge_detail_onefc_no_duplicates)

    # all edge detail on b benchmark from fca and fcb  ，each of them has no duplicated edge
    df_edge_detail_benchmark_no_dulicates = pd.concat(df_edge_detail_fcs_no_dulicates, ignore_index=True)
    df_edge_detail_benchmark_no_dulicates.to_csv(f"csv/fscve_edge_detail_{benchmark}.csv")
    print(df_edge_detail_benchmark_no_dulicates.shape[0])
    print("**" * 20)

    # # common edges of fca and fcb
    # df_edge_detail_benchmark_common = df_edge_detail_benchmark_no_dulicates[
    #     df_edge_detail_benchmark_no_dulicates.duplicated('edge', keep=False)]
    # list_edge_common = df_edge_detail_benchmark_common["edge"].to_list()
    # # print(list_edge_common)
    # # print(df_edge_detail_benchmark_common)
    # # print(df_edge_detail_benchmark_common.shape[0])
    #
    # print("--" * 20)
    # # all edge detail on b benchmark from fca and fcb
    # # df_edge_detail_benchmark = pd.concat(df_edge_detail_fcs, ignore_index=True)
    # # print(df_edge_detail_benchmark.shape[0])
    #
    # # calc the fuzzer combination's complementary measurement on a benchmakr during all of the repeated experiments
    # for fc in fcs:
    #     df_detail_fc_measurement = dict_fc_dataframe_detail[fc]
    #     df_detail_fc_measurement['fuzzer'] = df_detail_fc_measurement['fuzzer'].map(
    #         lambda x: re.findall(r"(.+?)-exid\d+", x)[0])
    #     # print(df_detail_fc.shape[0])
    #     # print(df_detail_fc_measurement)
    #     # print(df_detail_fc[df_detail_fc["edge"].isin(df_edge_detail_benchmark_common["edge"])].shape[0])
    #     df_detail_fc_measurement = df_detail_fc_measurement[df_detail_fc_measurement["edge"].isin(
    #         df_edge_detail_benchmark_common["edge"])]  # dataframe with edges in common
    #     count_series = df_detail_fc_measurement.groupby(
    #         by=["fuzzer", "edge"]).size()  # group and get the count of the same column value composition
    #     # print(count_series)
    #     df_detail_fc_measurement = count_series.to_frame(name='times').reset_index()
    #     # df_detail_fc_measurement = df_detail_fc_measurement[df_detail_fc_measurement["times"]>1]
    #     print(df_detail_fc_measurement)
    #
    #     # step2 is coming
    #     edges = df_detail_fc_measurement["edge"].unique().tolist()
    #     edge_complementary_measurement_fc = 0
    #     for edge in edges:
    #         # lc the probability to cover a special edge
    #         fuzzers = df_detail_fc_measurement["fuzzer"].unique().tolist()
    #         pe = 1
    #
    #         for fuzzer in fuzzers:
    #             # print(f"{fuzzer}----{edge}")
    #             tmp = df_detail_fc_measurement[
    #                 (df_detail_fc_measurement["fuzzer"] == f"{fuzzer}") & (
    #                         df_detail_fc_measurement["edge"] == f"{edge}")]
    #             # print(tmp)
    #             # print(tmp.empty)
    #             if tmp.empty or (pd.isnull(tmp.iloc[0, 2])):  # 3---times
    #                 continue
    #             pe = pe * (1 - tmp.iloc[0, 2] / expids)
    #
    #         edge_complementary_measurement_fc = edge_complementary_measurement_fc + 1 - pe
    #     dict_values_fc.append(fc)
    #     dict_values_complemetary_measurement.append(edge_complementary_measurement_fc)  # store the measurement metric
    #
    # dict_results_complemetary_measurement["fuzzer_combination"] = dict_values_fc
    # dict_results_complemetary_measurement["complemetary_metric"] = [
    #     (0 if len(list_edge_common) == 0 else i / len(list_edge_common)) for i in dict_values_complemetary_measurement]
    # df_results_complemetary_measurement = pd.DataFrame(dict_results_complemetary_measurement)
    # print(df_results_complemetary_measurement)
    # print(len(list_edge_common))
    # df_results_complemetary_measurement.to_csv(f"csv/fscve_edge_results_complemetary_metric_{benchmark}.csv")

    # complementary measurement
    # step1:search the edges that the two fuzzer combinations have found in total on a benchmark in all repeated experiments  ,that is fca:1,2,3,3  fcb:1,3,4,5,  ,the total unique element 1,2,3,4,5 would be collected
    #      merge the results of repeated experiments of a fuzzer combination（fc）on  a benchmark, collect the times each edge has been found by one fuzzer

    # step2:for each fuzzer combination(fc) ,calc its complementary measurement,by the formulation:  sum(1-II(1-pi))

    print("**" * 20)

    # common edges of fca and fcb
    df_edge_detail_benchmark_common = df_edge_detail_benchmark_no_dulicates.drop_duplicates(['edge'])
    list_edge_common = df_edge_detail_benchmark_common["edge"].to_list()
    # print(list_edge_common)
    # print(df_edge_detail_benchmark_common)
    # print(df_edge_detail_benchmark_common.shape[0])

    print("--" * 20)
    # all edge detail on b benchmark from fca and fcb
    # df_edge_detail_benchmark = pd.concat(df_edge_detail_fcs, ignore_index=True)
    # print(df_edge_detail_benchmark.shape[0])

    # calc the fuzzer combination's complementary measurement on a benchmakr during all of the repeated experiments
    for fc in fcs:
        df_detail_fc_measurement = dict_fc_dataframe_detail[fc]
        df_detail_fc_measurement['fuzzer'] = df_detail_fc_measurement['fuzzer'].map(
            lambda x: re.findall(r"(.+?)-exid\d+", x)[0])
        # print(df_detail_fc.shape[0])
        # print(df_detail_fc_measurement)
        # print(df_detail_fc[df_detail_fc["edge"].isin(df_edge_detail_benchmark_common["edge"])].shape[0])
        df_detail_fc_measurement = df_detail_fc_measurement[df_detail_fc_measurement["edge"].isin(
            df_edge_detail_benchmark_common["edge"])]  # dataframe with edges in common
        count_series = df_detail_fc_measurement.groupby(
            by=["fuzzer", "edge"]).size()  # group and get the count of the same column value composition
        # print(count_series)
        df_detail_fc_measurement = count_series.to_frame(name='times').reset_index()
        # df_detail_fc_measurement = df_detail_fc_measurement[df_detail_fc_measurement["times"]>1]
        print(df_detail_fc_measurement)

        # step2 is coming
        edges = df_detail_fc_measurement["edge"].unique().tolist()
        edge_complementary_measurement_fc = 0
        for edge in edges:
            # lc the probability to cover a special edge
            fuzzers = df_detail_fc_measurement["fuzzer"].unique().tolist()
            pe = 1

            for fuzzer in fuzzers:
                # print(f"{fuzzer}----{edge}")
                tmp = df_detail_fc_measurement[(df_detail_fc_measurement["fuzzer"] == f"{fuzzer}") & (
                        df_detail_fc_measurement["edge"] == f"{edge}")]
                # print(tmp)
                # print(tmp.empty)
                if tmp.empty or (pd.isnull(tmp.iloc[0, 2])):  # 3---times
                    continue
                pe = pe * (1 - tmp.iloc[0, 2] / expids)

            edge_complementary_measurement_fc = edge_complementary_measurement_fc + 1 - pe
        dict_values_fc.append(fc)
        dict_values_complemetary_measurement.append(edge_complementary_measurement_fc)  # store the measurement metric

    dict_results_complemetary_measurement["fuzzer_combination"] = dict_values_fc
    dict_results_complemetary_measurement["complemetary_metric"] = dict_values_complemetary_measurement
    df_results_complemetary_measurement = pd.DataFrame(dict_results_complemetary_measurement)
    # df_results_complemetary_measurement["complemetary_metric"] = df_results_complemetary_measurement[
    #     "complemetary_metric"].apply(0 if len(list_edge_common) == 0 else lambda x: x / len(list_edge_common))
    print(df_results_complemetary_measurement)
    df_results_complemetary_measurement.to_csv(f"csv/fscve_edge_results_complemetary_metric_{benchmark}.csv")

    print("+++" * 20)
    # calc the total unique edges of a fc on special benchmark
    # for enfuzz,the old data collected didn't include edge-coverage-fuzzer db table
    # so,it needs to obtain the info from edge-coverage-global,instead of fscve_edge_detail_{benchmark}_{fc}_{expid}.csv
    for fc in fcs:
        dfs = []
        for expid in range(0, expids):
            df = pd.read_csv(f"csv/fscve_step6_metric1_totalunique_{benchmark}_{fc}_{expid + 1}.csv")
            dfs.append(df)

        df_edge_total_unique_tmp = pd.concat(dfs, ignore_index=True)
        print(df_edge_total_unique_tmp.shape[0])
        df_edge_total_unique_tmp = df_edge_total_unique_tmp.drop_duplicates("edge")
        print(df_edge_total_unique_tmp.shape[0])
        df_edge_total_unique = pd.DataFrame(
            {"benchmark": [benchmark], "fuzzer_combination": [fc], "total_unique": [df_edge_total_unique_tmp.shape[0]]})
        print(df_edge_total_unique)
        df_edge_total_unique.to_csv(f"csv/fscve_step6_metric1_totalunique_{benchmark}_{fc}_all.csv")

    #calc for venn diagram for edge covered by fuzzers
    print("**" * 5, "calc for venn diagram for edge covered by fuzzers")
    cols_to_keep_edge_detail_venn = ["fuzzer", "edge"]
    df_edge_detail_fcs_no_dulicates_venn = []
    dict_values_fc_venn = []
    #calc all data of a fuzzer combination on one benchmark
    for fc in fcs:
        dfs_venn = []
        for expid in range(0,expids):
            df_venn = pd.read_csv(f"csv/fscve_edge_detail_{benchmark}_{fc}_{expid+1}.csv")
            df_venn["edge"] = df_venn["block_source"].astype("str") + df_venn["block_target"].astype("str").map(lambda x:"-"+x)
            dfs_venn.append(df_venn)
            # print(df)
        df_edge_detail_onefc_venn = pd.concat(dfs_venn, ignore_index=True)
        df_edge_detail_onefc_venn = df_edge_detail_onefc_venn.drop(df_edge_detail_onefc_venn.columns.difference(cols_to_keep_edge_detail_venn), axis=1).sort_values(by=["edge","fuzzer"])

        #edge coverage global history of one fuzzer combinations
        df_edge_detail_onefc_venn.to_csv(f"csv/fscve_step6_metric3_venn_{benchmark}_{fc}.csv")
        #print(df_edge_detail_onefc)
        df_edge_detail_onefc_venn["fuzzer"]=df_edge_detail_onefc_venn["fuzzer"].apply(lambda x:x[:x.rindex("-exid")])
        print("onefc detail-_venn----------------------------------------------------------")
        #print( df_edge_detail_onefc)
        #delete duplicated edges for every fuzzer combination and fuzzer
        print("aaaaa_venn", df_edge_detail_onefc_venn.shape[0])
        df_edge_detail_onefc_no_duplicates_venn = df_edge_detail_onefc_venn.drop_duplicates(['fuzzer','edge'])
        print("bbbbbb_venn", df_edge_detail_onefc_no_duplicates_venn.shape[0])
        df_edge_detail_onefc_no_duplicates_venn["fuzzer_combination"] = fc
        df_edge_detail_onefc_no_duplicates_venn["benchmark"] = benchmark
        #df_edge_detail_onefc_no_duplicates=df_edge_detail_onefc_no_duplicates.reset_index(drop=True)
        print(df_edge_detail_onefc_no_duplicates_venn)
        df_edge_detail_fcs_no_dulicates_venn.append(df_edge_detail_onefc_no_duplicates_venn)


    #all edge detail on b benchmark from fca and fcb  ，each of them has no duplicated edge
    df_edge_detail_benchmark_no_dulicates_venn = pd.concat(df_edge_detail_fcs_no_dulicates_venn, ignore_index=True)
    df_edge_detail_benchmark_no_dulicates_venn = df_edge_detail_benchmark_no_dulicates_venn.drop(df_edge_detail_benchmark_no_dulicates_venn.columns.difference(["benchmark","fuzzer_combination","fuzzer","edge"]), axis=1).sort_values(by=["benchmark","fuzzer_combination","fuzzer","edge"])
    df_edge_detail_benchmark_no_dulicates_venn.to_csv(f"csv/fscve_step6_metric3_venn_{benchmark}.csv")
    print(df_edge_detail_benchmark_no_dulicates_venn.shape[0])
    print("**"*20)

    print("************finished:fscve_step5_edge_coverage_analysis_repeated*********************")
