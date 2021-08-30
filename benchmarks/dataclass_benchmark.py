import numpy as np
from dataclasses import dataclass, field
import cProfile
import tqdm
import datetime
import time

import sys
sys.path.append('..')
import doctable
import timing


@doctable.schema
class DataObj:
    __slots__ = []
    id: int = doctable.Col()
    name1: str = doctable.Col()
    name2: str = doctable.Col()
    name3: str = doctable.Col()
    name4: str = doctable.Col()
    name5: str = doctable.Col()
    name6: str = doctable.Col()
    name7: str = doctable.Col()
    name8: str = doctable.Col()
    name9: str = doctable.Col()
    name10: str = doctable.Col()
    def __post_init__(self):
        if self.name1 is None:
            self.name1 = str(self.id)
            self.name2 = str(self.id)
            self.name3 = str(self.id)
            self.name4 = str(self.id)
            self.name5 = str(self.id)
            self.name6 = str(self.id)
            self.name7 = str(self.id)
            self.name8 = str(self.id)
            self.name9 = str(self.id)
            self.name10 = str(self.id)


if __name__ == '__main__':
    
    # create doctable
    folder = 'tmp_dataclass_benchmark'
    tmpf = doctable.TempFolder(folder)
    db = doctable.DocTable(schema=DataObj, target=f'{folder}/test.db', new_db=True)

    # make data payload
    payload = [DataObj(i) for i in range(100000)]
    dict_payload = [o._doctable_as_dict() for o in payload]
    
    print(f'==== DataClass ====')
    print(f'\t\tDataclass Insert: {timing.time_call(lambda: db.insert(payload))}')
    print(f'\t\tDataclass Select: {timing.time_call(lambda: db.select())}')
    db.delete()

    print(f'==== Dict ====')
    print(f'\t\tDict Insert: {timing.time_call(lambda: db.insert(dict_payload))}')
    print(f'\t\tDict Select: {timing.time_call(lambda: db.select(as_dataclass=False))}')
    db.delete()
