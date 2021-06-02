


class QueueInserter:
    ''' Used to manage queued bulk insertion program logic.
    '''
    def __init__(self, db, chunk_size=1, verbose=False, **insert_kwargs):
        self.db = db
        self.chunk_size = chunk_size
        self.verbose = verbose
        self.insert_kwargs = insert_kwargs
        self.queue = list() # record queue

    def insert(self, record):
        ''' Add a single record to the queue.
        '''
        self.queue.append(record)
        self.dump_check()
    
    def insert_many(self, records):
        ''' Insert multiple records into the queue.
        '''
        self.queue += list(records)
        self.dump_check()

    def dump_check(self):
        ''' Dump queue into database if meets threshold.
        '''
        if len(self.queue) >= self.chunk_size:
            self.dump()
    
    def dump(self):
        ''' Insert queue data.
        '''
        if len(self.queue) > 0:
            if self.verbose: print(f'Inserting {len(self.queue)} records.')
            self.db.insert(self.queue, **self.insert_kwargs)
            self.queue = list()

    def __del__(self):
        ''' Dump records before being deleted.
        '''
        self.dump()


