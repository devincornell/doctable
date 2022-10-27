from __future__ import annotations

import statistics
import typing
import dataclasses
import datetime
from ..stepper import Stepper, StepContext
from .unit_format import format_memory, format_time


@dataclasses.dataclass
class BenchResult:
    results: typing.List[BenchResultRun] = dataclasses.field(default_factory=list)
    
    def add_step_context(self, step_ctx: StepContext):
        self.results.append(BenchResultRun.from_step_context(step_ctx))
        
    def elapsed_summary(self, stat: typing.Callable = statistics.mean) -> datetime.timedelta:
        av_secs = stat([r.elapsed.total_seconds() for r in self.results])
        return datetime.timedelta(seconds=av_secs)
    
    def av_memory(self) -> int:
        return int(statistics.mean([r.memory_change for r in self.results]))
        
    def __repr__(self):
        time_av = format_time(self.elapsed_summary(statistics.mean).total_seconds())
        time_sd = format_time(self.elapsed_summary(statistics.stdev).total_seconds()) if len(self.results) > 1 else 0
        mem_av = format_memory(self.av_memory())
        return f'{self.__class__.__name__}({time_av=}, {time_sd=}, {mem_av=})'


@dataclasses.dataclass
class BenchResultRun:
    elapsed: datetime.timedelta
    elapsed_str: str
    memory_change: int
    memory_change_str: str
    
    @classmethod
    def from_step_context(cls, step_ctx: StepContext) -> BenchResult:
        return cls(
            elapsed = step_ctx.elapsed(),
            elapsed_str = step_ctx.elapsed_str(),
            memory_change = step_ctx.memory_change(),
            memory_change_str = step_ctx.start_memory_str(),
        )
    
class Benchmark:
    
    @classmethod
    def time_func_call(cls, func: typing.Callable, args: typing.Tuple = tuple(), kwargs: typing.Dict = None, num_calls: int = 1, as_str: bool = False, show_tqdm: bool = True):
        ''' Time function call with 0.05 ms latency per call.
        '''
        if kwargs is None:
            kwargs = dict()
        
        stepper = Stepper(verbose=False)
        result = BenchResult()
        for i in range(num_calls):
            with stepper.step() as step_ctx:
                func(*args, **kwargs)
                result.add_step_context(step_ctx)
        
        return result
        


