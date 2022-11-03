import argparse

from fscve_step1_db import AnalysisState, Dispatch, TestCase, EdgeCoverageFuzzer, Discovery, EdgeCoverageGlobal, \
    FuzzerEvent, FscveStep1DbHelper
from sqlalchemy import desc
import os
from pyutilszxy import walk_files


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
    bm = dbhelper.benchmark
    fc = dbhelper.fc

    print("***" * 10, f" fscve_step0_pre_data bm:{bm}----fc:{fc}---expid:{expid}start")

    query = session.query(Discovery).order_by(desc(Discovery.discovery_time)).first()
    print(query)

    query = session.query(Discovery.discovery_id).filter(Discovery.discovery_time > 86400).all()
    # print(query[0].discovery_id)
    # query all discoveries with time after 24h
    arr_discovery = [res.discovery_id for res in query]
    print(arr_discovery)

    # delete the records after 24h , from table analysis_states,edge_coverages_fuzzer,
    # edge_coverages_global,fuzzer_events,dispatch
    print(session.query(Dispatch.test_case_hash).filter(Dispatch.dispatch_time > 86400).all())
    session.query(Dispatch).filter(Dispatch.dispatch_time > 86400).delete(synchronize_session=False)
    session.commit()
    print("*******dispatch*******", session.query(Dispatch.test_case_hash).filter(Dispatch.dispatch_time > 86400).all())

    print("*******AnalysisState*******" * 6)
    print(session.query(AnalysisState.discovery_id).filter(AnalysisState.discovery_id.in_(arr_discovery)).all())
    session.query(AnalysisState).filter(AnalysisState.discovery_id.in_(arr_discovery)).delete(synchronize_session=False)
    session.commit()
    print("*******AnalysisState*******",
          session.query(AnalysisState.discovery_id).filter(AnalysisState.discovery_id.in_(arr_discovery)).all())

    print("*****EdgeCoverageFuzzer*********" * 6)
    print(session.query(EdgeCoverageFuzzer).filter(EdgeCoverageFuzzer.discovery_id.in_(arr_discovery)).all())
    session.query(EdgeCoverageFuzzer).filter(EdgeCoverageFuzzer.discovery_id.in_(arr_discovery)).delete(
        synchronize_session=False)
    session.commit()
    print("*******EdgeCoverageFuzzer*******",
          session.query(EdgeCoverageFuzzer.discovery_id).filter(EdgeCoverageFuzzer.discovery_id.in_(arr_discovery)).all())

    print("*******EdgeCoverageGlobal*******" * 6)
    print(session.query(EdgeCoverageGlobal).filter(EdgeCoverageGlobal.discovery_id.in_(arr_discovery)).all())
    session.query(EdgeCoverageGlobal).filter(EdgeCoverageGlobal.discovery_id.in_(arr_discovery)).delete(
        synchronize_session=False)
    session.commit()
    print("******EdgeCoverageGlobal********",
          session.query(EdgeCoverageGlobal.discovery_id).filter(EdgeCoverageGlobal.discovery_id.in_(arr_discovery)).all())

    print("FuzzerEvent" * 6)
    print(session.query(FuzzerEvent).filter(FuzzerEvent.event_time > 86400).all())
    session.query(FuzzerEvent).filter(FuzzerEvent.event_time > 86400).delete(synchronize_session=False)
    session.commit()
    print("*****FuzzerEvent*********", session.query(FuzzerEvent).filter(FuzzerEvent.event_time > 86400).all())

    print("******delete crash db cords and files after 24h ********start" * 3)
    query = session.query(Discovery.test_case_hash).filter(Discovery.discovery_time > 86400).all()
    # query all discoveries with time after 24h
    arr_test_case_hash = [res.test_case_hash for res in query]
    print(arr_test_case_hash)
    query = session.query(TestCase).filter(TestCase.hash.in_(arr_test_case_hash), TestCase.test_case_type_id == 2).all()
    array_crashes = [res.hash for res in query]

    # delete crash files after 24h
    crash_dir = f"runinfosqlites/{bm}/{fc}/{expid}/crashes"
    print(len(walk_files(crash_dir)))
    for crash in array_crashes:
        path = f"{crash_dir}/{crash}"
        if os.path.exists(path):
            os.remove(path)
        else:
            print('no such file:%s' % crash)
    print("after delete", len(walk_files(crash_dir)))

    # delete all testcases after 24h
    print("del testcase start", session.query(TestCase).filter(TestCase.hash.in_(arr_test_case_hash)).all())
    session.query(TestCase).filter(TestCase.hash.in_(arr_test_case_hash)).delete(synchronize_session=False)
    session.commit()
    print("del testcase end", session.query(TestCase).filter(TestCase.hash.in_(arr_test_case_hash)).all())

    print("******delete crash db records and files after 24h ********end" * 3)

    print("******delete discoveries after 24h ********start" * 3,
          len(session.query(Discovery.test_case_hash).filter(Discovery.discovery_time > 86400).all()))
    session.query(Discovery).filter(Discovery.discovery_time > 86400).delete(synchronize_session=False)
    session.commit()
    print("******delete discoveries after 24h ********end" * 3,
          len(session.query(Discovery.test_case_hash).filter(Discovery.discovery_time > 86400).all()))
    print("***" * 10, f" fscve_step0_pre_data bm:{bm}----fc:{fc}---expid:{expid}end")
