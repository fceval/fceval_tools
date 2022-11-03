import sys
import os
from pyutilszxy import walk_files

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import argparse
from fscve_step1_db import CrashAnalysis, FscveStep1DbHelper, Discovery, Fuzzer, TestCase, FuzzerType, TestCaseType
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fscve_step1_db import Discovery, Fuzzer, TestCase, FuzzerType, TestCaseType
#from pyvenn import venn


def autolabel(rects, texts):
    __i__ = 0
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x(), 1.05 * height, "{}\n{}".format(int(height), texts[__i__]), rotation=90)
        __i__ += 1


def parse_args():
    parser = argparse.ArgumentParser(
        description="you should add those parameter benchmark--m fuzzer_combination--bm experiment_id---expid")
    parser.add_argument('--bm', help="benchmark name")
    parser.add_argument('--fc', help="fuzzer_combination name")
    parser.add_argument('--expid', help="experiment id")
    args = parser.parse_args()
    return args


def crash_analysis_to_bug_tag(df):
    global dict_bug_tag, bug_tag
    print("-----", df)
    print("+++++", df.index.values)
    for row in df.index.values:
        print(row)
        print(df.loc[row, "crash_frames_hash"])
        print(dict_bug_tag.keys())
        if df.loc[row, "crash_frames_hash"] not in dict_bug_tag.keys():
            dict_bug_tag[df.loc[row, "crash_frames_hash"]] = bug_tag
            bug_tag += 1


if __name__ == '__main__':
    args = parse_args()
    dbhelper = FscveStep1DbHelper(args.bm, args.fc, args.expid, False)
    # expids = [i for i in range(1, 6)]  # 5-time experiment
    # benchmarks = {"nm", "objdump", "readelf", "size", "strings", "strip"}
    # fcs = {"fca", "fcb"}
    # for bm in benchmarks:
    #     for fc in fcs:
    #         for expid in expids:
    # dbhelper = FscveStep1DbHelper(bm, fc, expid, True)
    session = dbhelper.session
    expid = dbhelper.experiment_id
    benchmark = dbhelper.benchmark
    fc = dbhelper.fc
    # query = session.query(AnalysisState.analysis_id,AnalysisState.discovery_id).first()
    # print(query)
    print(f"{benchmark}---{fc}-----{expid}")

    # # calculate the total number of uniq crashes for step7 metric1
    # queryca = session.query(TestCase).filter(TestCase.test_case_type_id == 2).all()
    # dict_value_benchmark = [f"{benchmark}" for result in queryca]
    # dict_value_fc = [f"{fc}" for res in queryca]
    # dict_value_expid = [f"{expid}" for res in queryca]
    # dict_value_testcase_hash = [result.hash for result in queryca]
    #
    # dictca = {"benchmark": dict_value_benchmark, "fuzzer_combination": dict_value_fc, "expid": dict_value_expid,
    #           "testcase_hash": dict_value_testcase_hash}
    # df_unique_crashes = pd.DataFrame(dictca)
    # print(df_unique_crashes)
    # df_unique_crashes.to_csv(f"csv/fscve_unique_crashes_step7metric1_{benchmark}_{fc}_{expid}.csv")

    # calculate the total number of uniq real bugs
    queryca = session.query(CrashAnalysis).all()
    dict_value_crash_id = [result.crash_id for result in queryca]
    dict_value_testcase_hash = [result.test_case_hash for result in queryca]
    dict_value_crash_type = [result.crash_type for result in queryca]
    dict_value_frames_hash = [result.frames_hash for result in queryca]
    dictca = {"crash_id": dict_value_crash_id, "testcase_hash": dict_value_testcase_hash,
              "crash_type": dict_value_crash_type, "frames_hash": dict_value_frames_hash}
    df_crash_analysis = pd.DataFrame(dictca)
    # df_crash_analysis.set_index("crash_id")
    df_crash_group = df_crash_analysis.groupby(by="frames_hash")["frames_hash"].count()  # up by frames_hash
    print(df_crash_group)
    print("*" * 30)
    print("total number of unique bugs:", df_crash_group.count())

    dict_value_benchmark = [benchmark]
    dict_value_fuzzer_combination = [fc]
    dict_value_experiment_id = [expid]
    dict_value_bug_count = [df_crash_group.count()]
    df_bug_count = pd.DataFrame({"benchmark": dict_value_benchmark, "fuzzer_combination": dict_value_fuzzer_combination,
                                 "experiment_id": dict_value_experiment_id, "bug_count": dict_value_bug_count})
    df_bug_count.to_csv(f"csv/fscve_crash_analysis_bugcnt_{benchmark}_{fc}_{expid}.csv")
    print(df_bug_count)

    # ***********************************************************************
    # *************************************************************************
    # *************************************************************************
    # query the time of when which fuzzer uses which testcase to find which real bug ,triggered by which sanitizer
    querywftcbug = session.query(Discovery.discovery_id, Discovery.discovery_fuzzer, Fuzzer.fuzzer_name,
                                 FuzzerType.description.label("fuzzer_type_description"), Discovery.discovery_time,
                                 TestCase.hash.label("testcase_hash"),
                                 TestCaseType.description.label("testcase_type_description"), CrashAnalysis.crash_id,
                                 CrashAnalysis.crash_type, CrashAnalysis.frames_hash, CrashAnalysis.sanitizer)
    querywftcbug = querywftcbug.join((Fuzzer, Discovery.discovery_fuzzer == Fuzzer.fuzzer_id),
                                     (FuzzerType, Fuzzer.fuzzer_type_id == FuzzerType.id)).join(
        (TestCase, Discovery.test_case_hash == TestCase.hash),
        (TestCaseType, TestCase.test_case_type_id == TestCaseType.id))
    querywftcbug = querywftcbug.join(CrashAnalysis, Discovery.test_case_hash == CrashAnalysis.test_case_hash)
    querywftcbug = querywftcbug.filter(TestCaseType.id == 2).order_by(Discovery.discovery_time)

    # querywftcbug = querywftcbug.all()
    # print(querywftcbug)
    # print(querywftcbug.first().keys())
    dict_value_discovery_id = [result.discovery_id for result in querywftcbug]
    dict_value_discovery_fuzzer = [result.discovery_fuzzer for result in querywftcbug]
    dict_value_discovery_fuzzer_name = [result.fuzzer_name for result in querywftcbug]
    dict_value_fuzzer_type_description = [result.fuzzer_type_description for result in querywftcbug]
    dict_value_discovery_time = [result.discovery_time for result in querywftcbug]
    dict_value_testcase_hash = [result.testcase_hash for result in querywftcbug]
    dict_value_testcase_type_description = [result.testcase_type_description for result in querywftcbug]
    dict_value_crash_id = [result.crash_id for result in querywftcbug]
    # dict_value_crash_id.sort()
    # print(dict_value_crash_id)
    dict_value_crash_type = [result.crash_type for result in querywftcbug]
    dict_value_frames_hash = [result.frames_hash for result in querywftcbug]
    dict_value_sanitizer = [result.sanitizer for result in querywftcbug]
    dictwftcbug = {"discovery_id": dict_value_discovery_id, "discovery_fuzzer": dict_value_discovery_fuzzer,
                   "discovery_fuzzer_name": dict_value_discovery_fuzzer_name,
                   "fuzzer_type_description": dict_value_fuzzer_type_description,
                   "discovery_time": dict_value_discovery_time, "testcase_hash": dict_value_testcase_hash,
                   "testcase_type_description": dict_value_testcase_type_description, "crash_id": dict_value_crash_id,
                   "crash_type": dict_value_crash_type, "crash_frames_hash": dict_value_frames_hash,
                   "sanitizer": dict_value_sanitizer
                   }
    df_wftcbug = pd.DataFrame(dictwftcbug, index=dict_value_crash_id)

    df_wftcbug_fuzzers = df_wftcbug.drop_duplicates(
        ['discovery_fuzzer', 'crash_frames_hash'])  # record once for special fuzzer and real bug
    df_wftcbug_fuzzers = df_wftcbug_fuzzers.drop_duplicates('crash_id')  # remove duplicate crash_id,which is added to db unreasonably
    # print(df_wftcbug)
    df_wftcbug_fuzzers.to_csv(f"csv/fscve_crash_analysis_{benchmark}_{fc}_{expid}.csv")

    df_wftcbug_sanitizer = df_wftcbug.drop_duplicates(
        ['sanitizer', 'crash_frames_hash'])  # record once for special sanitizer and real bug
    df_wftcbug_sanitizer = df_wftcbug_sanitizer.drop_duplicates('crash_id')  # remove duplicate crash_id,which is added to db unreasonably
    # print(df_wftcbug_sanitizer)
    df_wftcbug_sanitizer["fuzzer_combination"] = [fc for idx in df_wftcbug_sanitizer["crash_id"]]
    df_wftcbug_sanitizer["benchmark"] = [benchmark for idx in df_wftcbug_sanitizer["crash_id"]]
    df_wftcbug_sanitizer.to_csv(f"csv/fscve_crash_analysis_step7_metric2_sanitizer_{benchmark}_{fc}_{expid}.csv")

    # ***********************************************************************
    # *************************************************************************
    # *************************************************************************
    # when the fuzzer combination finds the real bug first
    find_bug_first_cols_to_keep = ["crash_frames_hash", "discovery_time"]
    df_find_bug_first = df_wftcbug.drop_duplicates('crash_frames_hash')  # record once for special fuzzer and real bug
    df_find_bug_first = df_find_bug_first.drop(df_find_bug_first.columns.difference(find_bug_first_cols_to_keep),
                                               axis=1)
    df_find_bug_first["discovery_time"] = df_find_bug_first["discovery_time"] // 60  # minutes
    df_find_bug_first = df_find_bug_first.reset_index(drop=True)
    print(df_find_bug_first)
    df_find_bug_first.to_csv(f"csv/fscve_crash_analysis_bugfindfirsttime_{benchmark}_{fc}_{expid}.csv")

    # ***********************************************************************
    # *************************************************************************
    # *************************************************************************
    # visualize the history of the special fuzzer's bug findings

    print("""
       # ***********************************************************************
    # *************************************************************************
    # *************************************************************************
    # visualize the history of the special fuzzer's bug findings
    """
          )
    # tobal plot size setting
    plt.rcParams['figure.figsize'] = (38.4, 28.8)

    # visualize the history of the special fuzzer's bug findings
    array_count_by_time = []
    bugcnt = len(df_wftcbug)
    print(df_wftcbug)
    # ValueError: Can only compare identically-labeled Series objects
    df_wftcbug = df_wftcbug.reset_index(drop=True)

    # print(df_wftcbug)
    # df_wftcbug.to_csv("tmpcrash.csv")
    # print(df_wftcbug)
    # print("bugcnt:",bugcnt)
    # accumulate by time and fuzzer
    #for i in df_wftcbug['crash_id']:  # 0529
    for i in df_wftcbug.index.tolist():  # 0529
        # for i in range(0,len(df_wftcbug)):
        # print("i:",i,"*"*10,(df_wftcbug['discovery_time'] <= df_wftcbug.loc[i,'discovery_time']))
        # print(len(df_wftcbug[ (df_wftcbug['discovery_time'] <= df_wftcbug.loc[i,'discovery_time']) & (df_wftcbug['discovery_fuzzer_name'] == df_wftcbug.loc[i, 'discovery_fuzzer_name']) ]))
        tmp_time = df_wftcbug.loc[i, 'discovery_time']
        print(tmp_time)
        
        array_count_by_time.append(len(df_wftcbug[(df_wftcbug['discovery_time'].squeeze() <= tmp_time) & (
                df_wftcbug['discovery_fuzzer_name'] == df_wftcbug.loc[i, 'discovery_fuzzer_name'])]))
    # print(array_count_by_time)
    # print(dict_value_discovery_time)
    # print(dict_value_discovery_fuzzer_name)
    # print("*"*30)
    # sampling data every ten minutes
    df_plot = pd.DataFrame(
        {"bug_count": array_count_by_time, "discovery_time": [t // 60 for t in df_wftcbug['discovery_time']],
         "fuzzer": df_wftcbug['discovery_fuzzer_name']})
    print("-------", df_plot)
    fuzzers = df_wftcbug['discovery_fuzzer_name'].unique()
    df_top = pd.DataFrame({"bug_count": [0 for fuzzer in fuzzers], "discovery_time": [0 for fuzzer in fuzzers],
                           "fuzzer": df_wftcbug['discovery_fuzzer_name'].unique()})
    print("++++", df_top)
    df_plot = pd.concat([df_top, df_plot]).reset_index(drop=True)

    # ValueError: Can only compare identically-labeled Series objects
    df_plot.set_index("discovery_time")

    print(df_plot)

    # plt.figure(figsize=((df_plot.loc[df_plot["discovery_time"].last_valid_index(),"discovery_time"]+10)/60,6))
    # if no real bug,exit without drawing related pictures
    if df_crash_group.count() != 0:
        sns.set(style="whitegrid")
        # zhaoxy comment for temp solution
        # sns.set_palette(sns.color_palette("hls", len(df_wftcbug['discovery_fuzzer_name'].unique())))
        sns.lineplot(x="discovery_time", y="bug_count", hue="fuzzer", data=df_plot)
        sns.despine(right=True, top=True)

        # plt.xticks(ticks=range(0,df_plot.loc[df_plot["discovery_time"].last_valid_index(),"discovery_time"],20),rotation = 45)

        # zhaoxy comment for temp solution
        # plt.yticks(ticks=range(0, max(array_count_by_time) + 1, 1))

        plt.xlabel("Discovery Time (Minutes)")
        plt.ylabel("Bug Count")
        plt.title("Bug Discovery History", fontsize='xx-large', fontweight='heavy')
        plt.savefig(f"image/fuzzer_bug_history_{benchmark}_{fc}_{expid}.svg")
        # plt.show()  #for continuous batch operation

    # ***********************************************************************
    # *************************************************************************
    # *************************************************************************
    # function:which fuzzer finds the special bug earlist?
    # visualize when the real bug is found
    print("""
    # ***********************************************************************
    # *************************************************************************
    # *************************************************************************
    # function:which fuzzer finds the special bug earlist?
    # visualize when the real bug is found
    """
          )
    # query the time of when which fuzzer uses which testcase to find which real bug

    # if type(thisbar) == matplotlib.patches.Rectangle:

    # query the time of when which fuzzer uses which testcase to find which real bug
    querywftcbug = session.query(Discovery.discovery_id, Discovery.discovery_fuzzer, Fuzzer.fuzzer_name,
                                 FuzzerType.description.label("fuzzer_type_description"), Discovery.discovery_time,
                                 TestCase.hash.label("testcase_hash"),
                                 TestCaseType.description.label("testcase_type_description"), CrashAnalysis.crash_id,
                                 CrashAnalysis.crash_type, CrashAnalysis.frames_hash)
    querywftcbug = querywftcbug.join((Fuzzer, Discovery.discovery_fuzzer == Fuzzer.fuzzer_id),
                                     (FuzzerType, Fuzzer.fuzzer_type_id == FuzzerType.id)).join(
        (TestCase, Discovery.test_case_hash == TestCase.hash),
        (TestCaseType, TestCase.test_case_type_id == TestCaseType.id))
    querywftcbug = querywftcbug.join(CrashAnalysis, Discovery.test_case_hash == CrashAnalysis.test_case_hash)
    querywftcbug = querywftcbug.filter(TestCaseType.id == 2).order_by(Discovery.discovery_time)

    # querywftcbug = querywftcbug.all()
    # print(querywftcbug)
    # print(querywftcbug.first().keys())
    dict_value_discovery_id = [result.discovery_id for result in querywftcbug]
    dict_value_discovery_fuzzer = [result.discovery_fuzzer for result in querywftcbug]
    dict_value_discovery_fuzzer_name = [result.fuzzer_name for result in querywftcbug]
    dict_value_fuzzer_type_description = [result.fuzzer_type_description for result in querywftcbug]
    dict_value_discovery_time = [result.discovery_time for result in querywftcbug]
    dict_value_testcase_hash = [result.testcase_hash for result in querywftcbug]
    dict_value_testcase_type_description = [result.testcase_type_description for result in querywftcbug]
    dict_value_crash_id = [result.crash_id for result in querywftcbug]
    dict_value_crash_type = [result.crash_type for result in querywftcbug]
    dict_value_frames_hash = [result.frames_hash for result in querywftcbug]
    dictwftcbug = {"discovery_id": dict_value_discovery_id, "discovery_fuzzer": dict_value_discovery_fuzzer,
                   "discovery_fuzzer_name": dict_value_discovery_fuzzer_name,
                   "fuzzer_type_description": dict_value_fuzzer_type_description,
                   "discovery_time": dict_value_discovery_time, "testcase_hash": dict_value_testcase_hash,
                   "testcase_type_description": dict_value_testcase_type_description, "crash_id": dict_value_crash_id,
                   "crash_type": dict_value_crash_type, "crash_frames_hash": dict_value_frames_hash}
    df_wftcbug = pd.DataFrame(dictwftcbug, index=dict_value_crash_id)
    # df_wftcbug.set_index("crash_id")
    df_wftcbug = df_wftcbug.drop_duplicates(['crash_frames_hash'])  # record once for special fuzzer and real bug
    # print(df_wftcbug)
    df_plot = pd.DataFrame({"crash_id": ["bug{}".format(cid) for cid in df_wftcbug["crash_id"]],
                            "discovery_time": [t // 60 for t in df_wftcbug['discovery_time']],
                            "fuzzer": df_wftcbug['discovery_fuzzer_name']})
    print(df_plot)
    path_wftcbug_csv = f"csv/fscve_crash_earlist_{benchmark}_{fc}_{expid}.csv"

    df_plot.to_csv(path_wftcbug_csv)
    # zhaoxy comment for temp solution
    # # if no real bug,exit without drawing related pictures
    # if df_crash_group.count() != 0:
    #     sns.set(style="whitegrid")
    #     bar = sns.barplot(x="crash_id", y='discovery_time', data=df_plot, yerr=0.001)
    #     sns.despine()
    #     plt.title("The Time to Find The Special Bug")
    #     plt.ylabel("Discovery Time (Minutes)")
    #     plt.xlabel("Crash Id")
    #     plt.yticks(range(0, df_plot.loc[df_plot.last_valid_index(), 'discovery_time'] + 100, 50))
    #     plt.xticks(rotation=45)
    #     hatches = ['\\', '+', 'x', '\\', '*', '-']
    #     for i, thisbar in enumerate(bar.patches):
    #         print(thisbar)
    #         # Set a different hatch for each bar
    #         thisbar.set_hatch(hatches[i % len(hatches)])
    #
    #     # to specify which fuzzer find the bug earlist
    #     autolabel([thisbar for i, thisbar in enumerate(bar.patches)], df_plot["fuzzer"].to_list())
    #     print(f"image/fuzzer_bug_earlist_{benchmark}_{fc}_{expid}.svg")
    #     plt.savefig(f"image/fuzzer_bug_earlist_{benchmark}_{fc}_{expid}.svg")
    #     # plt.show()

    # ***********************************************************************
    # *************************************************************************
    # *************************************************************************
    # draw the venn diagram to visualize the unique or common bug findings
    print("""
    # ***********************************************************************
    # *************************************************************************
    # *************************************************************************
    # draw the venn diagram to visualize the unique or common bug findings
    """
          )
    dict_bug_tag = {}
    bug_tag = 1
    print(f"csv/fscve_crash_analysis_{benchmark}_{fc}_{expid}.csv")
    df_wftcbug_venn = pd.read_csv(f"csv/fscve_crash_analysis_{benchmark}_{fc}_{expid}.csv")
    df_wftcbug_venn.set_index(df_wftcbug_venn["crash_id"], inplace=True)
    print(df_wftcbug_venn.index)
    # df_wftcbug_venn = pd.read_csv(f"csv/fscve_crash_analysis_{benchmark}_{fc}_{expid}.csv")
    # print(df_wftcbug_venn["crash_id"])
    crash_analysis_to_bug_tag(df_wftcbug_venn)
    fuzzers = df_wftcbug_venn['discovery_fuzzer_name'].unique()
    print(fuzzers)

    if len(fuzzers) > 1:
        # print(fuzzers)
        # print(dict_bug_tag)
        dict_fuzzer_to_tags = {}

        # get bug tags for every fuzzer
        for fuzzer in fuzzers:
            tags = []
            df_tmp = df_wftcbug_venn[df_wftcbug_venn['discovery_fuzzer_name'] == fuzzer]
            for row in df_tmp['crash_id']:
                tag = dict_bug_tag[df_tmp.loc[row, "crash_frames_hash"]]
            if tag not in tags:
                tags.append(tag)
            dict_fuzzer_to_tags[fuzzer] = tags

        # limit fuzzer numbers to 6 for venn graphs
        if len(fuzzers) > 6:
            fuzzers = fuzzers[:6]

        fuzzer_count = len(fuzzers)
        # print(dict_fuzzer_to_tags)
        #venn_functions = [venn.venn2, venn.venn3, venn.venn4, venn.venn5, venn.venn6]
        #print(dict_fuzzer_to_tags)
        #print([dict_fuzzer_to_tags[fuzzer] for fuzzer in fuzzers])
        #labels = venn.get_labels([dict_fuzzer_to_tags[fuzzer] for fuzzer in fuzzers], fill=['number', 'percent'])
        #func = venn_functions[fuzzer_count - 2]
        #try:
        #    fig, ax = func(labels, names=fuzzers)
        #    fig.savefig(f'image/fuzzer_bug_venn_{benchmark}_{fc}_{expid}.svg', bbox_inches='tight')
        #except Exception as e:
        #    print(e)

    # # ***********************************************************************
    # # *************************************************************************
    # # *************************************************************************
    # # total number of unique crashe testcases,maybe the original crashes would lead to the same crashes ,
    # # the number is still essential for evaluating fuzzer combinations ,
    # # because some testcase would not be correctly validated by the addresssanitizer and other tools
    # print("""
    # # total number of unique crashe testcases,maybe the original crashes would lead to the same crashes ,
    # # the number is still essential for evaluating fuzzer combinations ,
    # # because some testcase would not be correctly validated by the addresssanitizer and other tools
    # """
    #       )
    # # total number of unique crashe testcases,maybe the original crashes would lead to the same crashes ,
    # # the number is still essential for evaluating fuzzer combinations ,
    # # because some testcase would not be correctly validated by the addresssanitizer and other tools
    # wav_path = f"runinfosqlites/{benchmark}/{fc}/{expid}/crashes"
    # FILES = walk_files(wav_path)
    # if not FILES:
    #     print("[Error] empty crash files? please check glob syntax!")
    #     # exit(1)
    # serie_unique_crashes = pd.Series([benchmark, fc, expid, len(FILES)],
    #                                  index=['benchmark', 'fuzzer_combination', 'experiment_id', 'count'])
    # print(serie_unique_crashes)
    # df_unique_crashes = pd.DataFrame()
    #
    # # transform serie to dataframe
    # stmp = serie_unique_crashes.to_frame()
    # s2 = pd.DataFrame(stmp.values.T, columns=stmp.index)
    # df_unique_crashes = pd.concat([df_unique_crashes, s2], ignore_index=True)
    # print(df_unique_crashes)
    # path_unique_crashes_csv = f"csv/fscve_unique_crashes_{benchmark}_{fc}_{expid}.csv"
    # df_unique_crashes.to_csv(path_unique_crashes_csv)
    #
    # # # if no real bug,exit without drawing related pictures
    # # if df_crash_group.count() == 0:
    # #     sys.exit(0)

    print("************finished:fscve_step4_crash_analysis*********************")
