
import os
import dataclasses
import datetime

import doctable.util

from .messaging import BaseMessage, MessageType


@doctable.util.slots_dataclass
class WorkerStatus(BaseMessage):
    '''Status information sent from WorkerProcess to WorkerResource.
    '''
    __slots__ = []
    message_type = MessageType.STATUS

    pid: int = os.getpid()
    start_ts: int = dataclasses.field(default_factory=datetime.datetime.now)
    time_waiting: int = 0
    time_working: int = 0
    jobs_finished: int = 0
    uptime: int = None # to be updated before sending

    def update_uptime(self):
        self.uptime = datetime.datetime.now() - self.start_ts

    def efficiency(self):
        return self.time_working / (self.time_working + self.time_waiting)

    def total_efficiency(self):
        return self.time_working / self.uptime.total_seconds()

    def sec_per_job(self):
        return self.time_working / self.jobs_finished


