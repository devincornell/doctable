from dataclasses import dataclass

import sys
sys.path.append('..')
import doctable

@dataclass
class SimpleData:
    name: str
    age: int = 10
    
    @property
    def d(self):
        return self.__dict__

def test_doctablemongo():
    db = doctable.DocTableMongo('test', 'tester')
    
    # access property of pymongo.Collection through getattr
    assert(db.full_name=='test.tester')

    # access property of pymongo through getitem
    assert(db['full_name']=='test.tester')
    #assert(not hasattr(db, 'full_name'))
    
    # assign property of DocTableMongo
    db.full_name = 'whatever ye say'

    # verify that property of DocTableMongo was overwritten
    assert(db.full_name == 'whatever ye say')
    
    # .. but not the property of the underlying Collection
    assert(db['full_name']=='test.tester')

    data = SimpleData('my name')
    db.insert(data.__dict__)

    datas = [SimpleData(f'{i}').__dict__ for i in range(2000)]
    db.insert(datas)
    print(f'inserted {db.count_documents({})} docs.')

    db.delete_many({})
    print(f'after deleting there are {db.count_documents({})} docs.')


if __name__ == '__main__':

    test_doctablemongo()