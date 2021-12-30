
import os
import psutil
import dataclasses
import datetime
import typing
import doctable.util
import pandas as pd
import time

from .messaging import BaseMessage, MessageType

import enum
class TimerStat(enum.Enum):
    '''Represents the stat that the timer is currently measuring in the context manager.
    '''
    WAITING = enum.auto()
    WORKING = enum.auto()

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

    # used by contextmanager
    tmp_start: int = None
    current_measurement: TimerStat = None

    ############### for populating attributes in worker process ###############

    def update(self):
        '''Update uptime and memory usage info.
        '''
        self.uptime = datetime.datetime.now() - self.start_ts
        self.memory = psutil.Process(self.pid).memory_info()

    def __enter__(self):
        self.tmp_start = time.time()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.current_measurement is TimerStat.WORKING:
            self.time_working += time.time() - self.tmp_start
            self.jobs_finished += 1
        
        elif self.current_measurement is TimerStat.WAITING:
            self.time_waiting += time.time() - self.tmp_start

        self.current_measurement = None
        self.tmp_start = None
    
    def waiting(self):
        '''Sets up context manager to measure wait time.
        '''
        self.current_measurement = TimerStat.WAITING
        return self

    def working(self):
        '''Sets up context manager to measure wait time.
        '''
        self.current_measurement = TimerStat.WORKING
        return self

    

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

class DisabledWorkerStatus(WorkerStatus):
    '''Status object that has been disabled.
    '''
    def update(self):
        return
    
    def waiting(self):
        return self
    
    def working(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        pass
