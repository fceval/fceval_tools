import argparse

from sqlalchemy import ForeignKey, MetaData, create_engine, Column, Integer, String, LargeBinary, UniqueConstraint, REAL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base_overhead = declarative_base()


class OverheadRecord(Base_overhead):
    __tablename__ = 'overhead_record'
    overhead_id = Column(Integer(), primary_key=True, autoincrement=True)
    container_name = Column(String(50))
    cpu_usage = Column(REAL())
    mem_used = Column(REAL())
    mem_total = Column(REAL())
    mem_usage = Column(REAL())
    netin = Column(REAL())
    netout = Column(REAL())
    diskin = Column(REAL())
    diskout = Column(REAL())
    pids = Column(Integer())
    record_time = Column(Integer())

    def __repr__(self):
        return "(overhead_id={self.overhead_id}, " \
               "container_name={self.container_name})" \
               "cpu_usage={self.cpu_usage})" \
               "mem_used={self.mem_used})" \
               "mem_total={self.mem_total})" \
               "mem_usage={self.mem_usage})" \
               "netin={self.netin})" \
               "netout={self.netout})" \
               "diskin={self.diskin})" \
               "diskout={self.diskout})" \
               "pids={self.pids})" \
               "record_time={self.record_time})".format(self=self)


# def main():
# db overhead ,computer resources
metadata_overhead = MetaData()
engine_overhead = create_engine('sqlite:///overhead_record.sqlite', echo=False)
Session_overhead = sessionmaker(bind=engine_overhead)
session_overhead = Session_overhead()
Base_overhead.metadata.create_all(engine_overhead)


# if __name__ == '__main__':
    # main()
