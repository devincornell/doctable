import sys
sys.path.append('..')
import doctable

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




if __name__ == '__main__':

    test_doctablemongo()