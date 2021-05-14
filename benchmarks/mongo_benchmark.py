import numpy as np
from dataclasses import dataclass, field
import cProfile
import tqdm
import datetime
import time
import pymongo

import sys
sys.path.append('..')
import doctable
import timing


@dataclass
class DataObj(doctable.DocTableSchema):
    arc: int = doctable.Col()
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
        if self.name1 == doctable.EmptyValue():
            self.name1 = str(self.arc)
            self.name2 = str(self.arc)
            self.name3 = str(self.arc)
            self.name4 = str(self.arc)
            self.name5 = str(self.arc)
            self.name6 = str(self.arc)
            self.name7 = str(self.arc)
            self.name8 = str(self.arc)
            self.name9 = str(self.arc)
            self.name10 = str(self.arc)


if __name__ == '__main__':
    timer = doctable.Timer()
    
    timer.step('creating db')
    folder = 'tmp_mongo'
    tmpf = doctable.TempFolder(folder)
    db = doctable.DocTable(schema=DataObj, target=f'{folder}/test.db', new_db=True)
    db.delete()

    timer.step('creating mongo db')
    myclient = pymongo.MongoClient("mongodb://localhost:27017")
    ndb = myclient["nonprofits"]
    test_col = ndb["test"]
    #test_col.delete_many({})
    print(f'mongo contents: {test_col.count_documents({})}')


    for num_entries in [10, 100, 1000, 10000]:
        print(f'===== Payload size {num_entries} =====')
        print('\tmaking data payload')
        payload = [DataObj(i) for i in range(num_entries)]
        payload_dict = [o._doctable_as_dict() for o in payload]

        print('\ttesting inserts')
        print(f'\tsqlite insert: {timing.time_call(lambda: db.insert(payload_dict), num_calls=1)}')
        print(f'\tmongo insert: {timing.time_call(lambda: test_col.insert_many(payload_dict), num_calls=1)}')
        db.delete()
        test_col.delete_many({})
    print()
    
