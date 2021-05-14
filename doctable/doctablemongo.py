
import pymongo
#from doctable.util.staticargparser import StaticArgParser

class DocTableMongo:
    def __init__(self, db: str=None, collection: str=None, port: int = 27017):
        ''' Interface for single MongoDB collection.
        '''
        self.client = pymongo.MongoClient(f"mongodb://localhost:{port}/")
        if db is not None:
            self.db = self.client[db]
        elif hasattr(self, '_db_'):
            self.db = self.client[self.__db__]
        else:
            raise ValueError('db must be provided in constructor or '
                                '_db_ must be defined.')

        if collection is not None:
            self.coll = self.db[collection]
        elif hasattr(self, '_collection_'):
            self.coll = self.db[self._collection_]
        else:
            raise ValueError('collection must be provided in constructor or '
                                '_collection_ must be defined.')

    ############################# Dunderscore Methods ##################
    def __getitem__(self, ind):
        ''' Get property of collection if not defined in this class.
        '''
        return getattr(self.coll, ind)

    def __setitem__(self, ind, val):
        ''' Set property of collection.
        '''
        return setattr(self.coll, ind, val)

    def __getattr__(self, ind):
        ''' Access property of this class or the collection.
        '''
        return getattr(self.coll, ind)

    ############################# CRUD Methods ##################
    def insert(self, data, **kwargs):
        if isinstance(data, dict):
            result = self.coll.insert_one(data)
        else:
            result = self.coll.insert_many()
        return result

    ############################# Other Access Methods ##################







