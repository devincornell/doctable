
import doctable
import typing

class ParseProcess:
    table: doctable.DocTable = None
        
    def __init__(self, parse_func: typing.Callable, table_cls, *table_args, **table_kwargs):
        '''Store info to construct the table.
        '''
        self.parse_func = parse_func
        self.table_cls = table_cls
        self.table_args = table_args
        self.table_kwargs = table_kwargs
        
    def connect_db(self):
        '''Make a new connection to the database and return the associated table.
        '''
        if self.table is None:
            self.table = self.table_cls(*self.table_args, **self.table_kwargs)
        return self.table
    
    def __call__(self, text):
        '''Execute function in worker process.
        '''
        table = self.connect_db()
        #record = 
        record = NewsgroupDoc.from_string(text)
        table.insert(record)


