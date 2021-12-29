
import os
import psutil
import dataclasses
import datetime
import typing
import doctable.util
import pandas as pd

from .messaging import BaseMessage, MessageType


@doctable.util.slots_dataclass
class WorkerStatus(BaseMessage):
    '''Status information sent from WorkerProcess to WorkerResource.
    '''
    __slots__ = []
    message_type = MessageType.STATUS

    pid: int = os.getpid()

    # time-related fields
    start_ts: int = dataclasses.field(default_factory=datetime.datetime.now)
    time_waiting: int = 0
    time_working: int = 0
    jobs_finished: int = 0

    # to be populated with call to .update()
    uptime: int = None # to be updated before sending
    memory: typing.NamedTuple = None # result of call from .memory_info()

    def update(self):
        '''Update uptime and memory usage info.
        '''
        self.uptime = datetime.datetime.now() - self.start_ts
        self.memory = psutil.Process(self.pid).memory_info()

    def efficiency(self):
        return self.time_working / (self.time_working + self.time_waiting)

    def total_efficiency(self):
        return self.time_working / self.uptime.total_seconds()

    def sec_per_job(self):
        if self.jobs_finished > 0:
            return self.time_working / self.jobs_finished
    
    def as_series(self):
        '''Get the current information as a pandas series object for printing.
        '''
        return pd.Series({
            'start_ts': self.start_ts,
            'uptime': self.uptime,
            'jobs_finished': self.jobs_finished,
            'time_waiting (sec)': self.time_waiting,
            'time_working (sec)': self.time_working,
            'memory (MB)': self.memory.rss/1e6,
            'efficiency (%)': self.efficiency()*100,
            'total_efficiency (%)': self.total_efficiency()*100,
            'sec_per_job (sec)': self.sec_per_job(),
        })


