
'''
This file contains functions for migrating database tables.
This means adding or removing columns, etc.
'''
from .connectengine import ConnectEngine

from .doctable import DocTable

def list_tables(target=':memory:', dialect='sqlite', **engine_args):
    ''' List tables in an sqlite database.
    Args:
        target (str): sql file or endpoint to connect to
        dialect (str): sql dialect to use for conenction
        engine_args (kwargs): passed to sqlalchemy ConnectEngine
    '''
    engine = ConnectEngine(target=target, dialect=dialect, **engine_args)
    return engine.list_tables()


def migrate_db(oldfname, newfname, newschema, newcolmap={}, delcols=[]):
    '''Moves old database to db with new schema.
    Args:
        oldfname (str): filename of old database.
        newfname (str): filename of new database.
        newschema (list<list>): shema that would be 
            used in the constructor to a doctable
            instance.
        newcolmap (dict<colname->func>): Allows for 
            population of new columns if they are a function 
            of the associated row.
    '''
    # connects to db without providing a schema, so will 
    # infer
    odb = DocTable(fname=oldfname)
    oldcols = set(odb.schemainfo.keys())
    
    ndb = DocTable(newschema, fname=newfname)
    newcols = set(ndb.schemainfo.keys())
    if ndb.count() > 0 and not append:
        raise ValueError('The new database target already has '
            'some entries. Set append=True to allow.')
    
    # add common columns
    commoncols = oldcols | newcols
    for orow in odb.select():

        newrow = {cn:cv for cn,cv in orow.items() if cn in commoncols}
        
        # add new columns by mapping old row
        if newcolmap is not None:
            for nc,ncfunc in newcolmap.items():
                newrow[nc] = ncfunc(newrow)
                
        # delete keys that might collide (specified in constructor)
        newrow = {cn:cv for cn,cv in newrow.items() if cn not in delcols}
        
        # add to db
        ndb.insert(dict(newrow))
    
