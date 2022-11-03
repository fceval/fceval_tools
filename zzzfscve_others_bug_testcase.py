import argparse
import os
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from fscve_step1_db import FscveStep1DbHelper
from fscve_step1_db import Discovery, Fuzzer, TestCase, FuzzerType, TestCaseType, CrashAnalysis
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(
        description="you should add those parameter benchmark--m fuzzer_combination--bm experiment_id---expid")
    parser.add_argument('--bm', help="benchmark name")
    parser.add_argument('--fc', help="fuzzer_combination name")
    parser.add_argument('--expid', help="experiment id")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    dbhelper = FscveStep1DbHelper(args.bm, args.fc, args.expid, False)
    session = dbhelper.session
    expid = dbhelper.experiment_id
    benchmark = dbhelper.benchmark
    fc = dbhelper.fc

    print(f"{benchmark}----{fc}----{expid}")
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
    # dict_value_crash_id.sort()
    # print(dict_value_crash_id)
    dict_value_crash_type = [result.crash_type for result in querywftcbug]
    dict_value_frames_hash = [result.frames_hash for result in querywftcbug]
    dict_value_benchmark = [benchmark for result in querywftcbug]
    dict_value_fc = [fc for result in querywftcbug]
    dict_value_expid = [expid for result in querywftcbug]
    dictwftcbug = {"benchmark": dict_value_benchmark, "fc": dict_value_fc, "expid": dict_value_expid,
                   "discovery_id": dict_value_discovery_id, "discovery_fuzzer": dict_value_discovery_fuzzer,
                   "discovery_fuzzer_name": dict_value_discovery_fuzzer_name,
                   "fuzzer_type_description": dict_value_fuzzer_type_description,
                   "discovery_time": dict_value_discovery_time, "testcase_hash": dict_value_testcase_hash,
                   "testcase_type_description": dict_value_testcase_type_description, "crash_id": dict_value_crash_id,
                   "crash_type": dict_value_crash_type, "crash_frames_hash": dict_value_frames_hash}
    df_wftcbug = pd.DataFrame(dictwftcbug, index=dict_value_crash_id)

    df_wftcbug = df_wftcbug.drop_duplicates(['crash_frames_hash'])  # record once for special fuzzer and real bug
    df_wftcbug = df_wftcbug.drop_duplicates('crash_id')  # remove duplicate crash_id,which is added to db unreasonably
    cols_to_keep = ["benchmark", "fc", "expid", "discovery_id", "testcase_hash", "crash_type", "crash_frames_hash"]
    df_wftcbug.drop(df_wftcbug.columns.difference(cols_to_keep), axis=1, inplace=True)
    # print(df_wftcbug)
    path_wftcbug_csv = f"csvzzzbugcase/{benchmark}_{fc}_{expid}.csv"
    df_wftcbug.to_csv(path_wftcbug_csv)
