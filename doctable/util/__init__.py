
from .io import read_pickle, write_pickle, read_json, write_json
from .showstopper import showstopper
#from .stepper import Stepper
from .fsstore import FSStore
from .distribute import Distribute
#from .tempfolder import TempFolder
from .unit_format import format_memory, format_time
from .chunking import chunk_slice, chunk
from .slots import slots_dataclass
from .logstep import LogStep, LogStepDiff
from .queueinserter import QueueInserter
from .benchmark import *
from .typechecks import *
from .asserts import *
from .iterfuncs import *

def parse_static_arg(obj, arg_value: typing.Any, arg_name: str, static_arg_name: str, default: bool = 1321566541214):
    if arg_value is None:
        try:
            #print(f'returning {getattr(obj, static_arg_name)=}')
            return getattr(obj, static_arg_name)
        except AttributeError as e:
            if default == 1321566541214:
                raise ValueError(f'Need to provide either {arg_name} or '
                    f'set .{static_arg_name}') from e
            else:
                return default
    else:
        if hasattr(obj, static_arg_name):
            raise ValueError(f'Cannot both provide {arg_name} and set '
                f'{static_arg_name}.')
        else:
            #print(f'returning {arg_value=}')
            return arg_value
