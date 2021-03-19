
import glob
import random
import os

from .pickling import read_pickle, write_pickle

class FSStore:
    ''' Class for storing and retriving records as pickle files.
    Useful in multi-threading applications where a direct database
        insertion for each process would cause too much blocking.
    '''
    def __init__(self, folder, records=None, save_every=10000, seed_range=100000000, check_collision=True):

        self.save_every = save_every
        self.folder = folder
        self.check_collision = check_collision

        if records is not None:
            self.records = list(records)
        else:
            self.records = list()
        
        # make folder if it does not exist
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)

        # set random seeds for filename purposes
        # (2x bc lower probability of collision)
        self.seed = random.randrange(seed_range/10, seed_range)
        self.seed += random.randrange(seed_range/10, seed_range)
        self.ct = 0

    def __del__(self):
        ''' Save buffer before being deleted.
        '''
        self.dump_file()

    def insert(self, record):
        ''' Add a single record.
        '''
        self.records.append(record)
        self.ct += 1

        if self.ct % self.save_every == 0:
            self.dump_file()

    def dump_file(self):
        ''' Save records to file and empty container.
        '''
        
        if len(self.records):
            fname = self.get_fname()
            if self.check_collision and os.path.exists(fname):
                raise FileExistsError(f'There was a collision in FSStore '
                            f'with seed={self.seed}, count={self.ct}, fname={fname}')
            
            write_pickle(self.records, fname)
        self.records = list()

    def get_fname(self):
        return f'{self.folder}/{self.seed+self.ct}.pic'

    def get_exist_fnames(self):
        return glob.glob(f'{self.folder}/*.pic')

    def select_chunks(self):
        ''' Yield records in file-sized chunks.
        '''
        for fname in self.get_exist_fnames():
            yield read_pickle(fname)
    
    def yield_records(self):
        ''' Reads pickle records and yields them one at a time.
        '''
        for records in self.select_chunks():
            for rec in records:
                yield rec
    
    def read_all_records(self):
        ''' Creates list of records from .yield_records()
        '''
        return list(self.yield_records())

    def delete_all(self):
        for fname in self.get_exist_fnames():
            os.remove(fname)
    
    #def make_record_md5(self, obj):
    #    return hashlib.md5(bin(self.records)).hexdigest()

    
















