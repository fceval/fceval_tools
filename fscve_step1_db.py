import argparse

from sqlalchemy import ForeignKey, MetaData, create_engine, Column, Integer, String, LargeBinary, UniqueConstraint, \
    REAL, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AnalysisState(Base):
    __tablename__ = 'analysis_states'
    discovery_id = Column(String(50), ForeignKey('discoveries.discovery_id'), index=True, primary_key=True)
    analysis_id = Column(Integer, ForeignKey('analysis_types.id'), index=True, primary_key=True)  # 联合索引，联合主键

    analysis_dump = Column(LargeBinary)  # 对应blob
    UniqueConstraint('discovery_id', 'analysis_id')  # 联合唯一

    def __repr__(self):
        return "AnalysisState(analysis_id ='{self.analysis_id}', " \
               "discovery_id='{self.discovery_id}', " \
               "analysis_dump='{self.analysis_dump}', ".format(self=self)


class AnalysisType(Base):
    __tablename__ = 'analysis_types'

    id = Column(Integer(), primary_key=True)
    needs_duplicates = Column(Integer())
    description = Column(String(50))

    def __repr__(self):
        return "AnalysisType(id ='{self.id}', " \
               "needs_duplicates='{self.needs_duplicates}', " \
               "description='{self.description}', ".format(self=self)


class CrashAnalysis(Base):
    __tablename__ = 'crash_analysis'
    crash_id = Column(Integer(), primary_key=True, autoincrement=True)
    test_case_hash = Column(String(50), ForeignKey('test_cases.hash'))
    crash_type = Column(String(50))
    frames_hash = Column(String(50))
    sanitizer = Column(String(5))

    def __repr__(self):
        return "crashid(hash={self.crash_id}, " \
               "test_case_hash={self.test_case_hash})" \
               "crash_type={self.crash_type})" \
               "sanitizer={self.sanitizer})" \
               "frames_hash={self.frames_hash})".format(self=self)


class Discovery(Base):
    __tablename__ = 'discoveries'
    discovery_id = Column(Integer(), primary_key=True, autoincrement=True)
    test_case_hash = Column(String(50), ForeignKey('test_cases.hash'), index=True)
    discovery_fuzzer = Column(Integer(), ForeignKey('fuzzers.fuzzer_id'), index=True)
    discovery_time = Column(Integer())
    is_new = Column(Integer())
    __table_args__ = (
        # PrimaryKeyConstraint('test_case_hash', 'discovery_fuzzer'), # 复合主键
        UniqueConstraint('test_case_hash', 'discovery_fuzzer'),  # 复合唯一
        {},
    )

    def __repr__(self):
        return "Discovery(discovery_id={self.discovery_id}, " \
               "test_case_hash={self.test_case_hash}, " \
               "discovery_fuzzer={self.discovery_fuzzer}, " \
               " discovery_time={self.discovery_time}, " \
               "is_new={self.is_new})".format(self=self)


class Dispatch(Base):
    __tablename__ = 'dispatch'
    test_case_hash = Column(String(50), ForeignKey('test_cases.hash'), primary_key=True)
    fuzzer_id = Column(Integer(), ForeignKey('fuzzers.fuzzer_id'), index=True)
    dispatch_time = Column(Integer())

    def __repr__(self):
        return "Dispatch(test_case_hash={self.test_case_hash}, " \
               "fuzzer_id={self.fuzzer_id}, " \
               "dispatch_time={self.dispatch_time})".format(self=self)


class EdgeCoverageFuzzer(Base):
    __tablename__ = 'edge_coverages_fuzzer'
    discovery_id = Column(Integer(), primary_key=True)
    discovery_fuzzer_id = Column(Integer(), ForeignKey('fuzzers.fuzzer_id'))
    block_source = Column(Integer())
    block_target = Column(Integer())

    def __repr__(self):
        return "Discovery(discovery_id={self.discovery_id}, " \
               "discovery_fuzzer_id={self.discovery_fuzzer_id}, " \
               "block_source={self.block_source}, " \
               "block_target={self.block_target})".format(self=self)


class EdgeCoverageGlobal(Base):
    __tablename__ = 'edge_coverages_global'
    discovery_id = Column(Integer(), primary_key=True)
    block_source = Column(Integer())
    block_target = Column(Integer())

    def __repr__(self):
        return "Discovery(discovery_id={self.discovery_id}, " \
               "block_source={self.block_source}, " \
               "block_target={self.block_target})".format(self=self)


class FuzzerEventType(Base):
    __tablename__ = 'fuzzer_event_types'
    id = Column(Integer(), primary_key=True)
    description = Column(String(50))

    def __repr__(self):
        return "FuzzerEventType(id={self.id}, " \
               "description={self.description}, ".format(self=self)


class FuzzerEvent(Base):
    __tablename__ = 'fuzzer_events'
    fuzzer_id = Column(Integer(), ForeignKey('fuzzers.fuzzer_id'), primary_key=True)
    event_type_id = Column(Integer(), ForeignKey('fuzzer_event_types.id'), primary_key=True)
    event_time = Column(Integer())

    def __repr__(self):
        return "FuzzerEvent(fuzzer_id={self.fuzzer_id}, " \
               "event_type_id={self.event_type_id}, " \
               "event_time={self.event_time})".format(self=self)


class FuzzerType(Base):
    __tablename__ = 'fuzzer_types'
    id = Column(Integer(), primary_key=True)
    description = Column(String(50))

    def __repr__(self):
        return "FuzzerType(id={self.id}, " \
               "description={self.description})".format(self=self)


class Fuzzer(Base):
    __tablename__ = 'fuzzers'
    fuzzer_id = Column(Integer(), primary_key=True)
    fuzzer_name = Column(String(20))
    fuzzer_type_id = Column(Integer(), ForeignKey('fuzzer_types.id'))

    def __repr__(self):
        return "Fuzzer(fuzzer_id={self.fuzzer_id}, " \
               "fuzzer_type_id={self.fuzzer_type_id})".format(self=self)


class TestCaseType(Base):
    __tablename__ = 'test_case_types'
    id = Column(Integer(), primary_key=True)
    description = Column(String(50))

    def __repr__(self):
        return "TestCaseType(id={self.id}, " \
               "description={self.description}, ".format(self=self)


class TestCase(Base):
    __tablename__ = 'test_cases'
    hash = Column(String(50), primary_key=True, index=True, unique=True)
    test_case_type_id = Column(Integer(), ForeignKey('test_case_types.id'))

    def __repr__(self):
        return "TestCase(hash={self.hash}, " \
               "test_case_type_id={self.test_case_type_id})".format(self=self)


class FscveStep1DbHelper(object):
    # benchmark:program under test
    # fc:fuzzer binations
    # experiment_id: the experiment sequence number of repeated experiments
    def __init__(self, benchmark, fc, experiment_id, echo=False):
        # engine = create_engine(
        #      f'sqlite:////home/kakaxdu/prjdataspell/casefc/runinfosqlites/{benchmark}/{fc}/{experiment_id}/run_info.sqlite', echo=echo)
        self.engine = create_engine(
            f'sqlite:///runinfosqlites/{benchmark}/{fc}/{experiment_id}/run_info.sqlite', echo=echo)
        # sql = text('DROP TABLE IF EXISTS crash_analysis;')
        # self.engine.execute(sql)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.experiment_id = experiment_id
        self.benchmark = benchmark
        self.fc = fc
        Base.metadata.create_all(self.engine)


# session = None
# expid = 1
#
#
# def main(args):
#     # global session
#     # global experiment_id
#     # print(f'Beginning to db analysis{args.experiment_id} ', flush=True)
#     # metadata = MetaData()
#     # # engine = create_engine('sqlite:///run_info.sqlite.1.casefc', echo=False)
#     # engine = create_engine(
#     #     f'sqlite:////home/kakaxdu/prjdataspell/casefc/runinfosqlites/{args.experiment_id}/run_info.sqlite', echo=False)
#     # # engine = create_engine('sqlite:////runinfosqlites/1/run_info.sqlite.1.casefc', echo=False)
#     #
#     # Session = sessionmaker(bind=engine)
#     # session = Session()
#     # experiment_id = args.experiment_id
#     #
#     # Base.metadata.create_all(engine)
#     global session
#     global expid
#     dbhelper = FscveStep1DbHelper(2, "", True)
#     query = dbhelper.session.query(AnalysisState.analysis_id, AnalysisState.discovery_id).first()
#     session = dbhelper.session
#     expid = dbhelper.experiment_id
#     print(query)
#
#
# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument('experiment_id', default=1)
#     args = parser.parse_args()
#     main(args)


# dbhelper = FscveStep1DbHelper("objdump", "fcb",  2, False)
# session = dbhelper.session
# expid = dbhelper.experiment_id
# benchmark = dbhelper.benchmark
# fc = dbhelper.fc
