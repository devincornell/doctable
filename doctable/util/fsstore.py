
import glob
import random
import os

from .io import read_pickle, write_pickle, read_json, write_json

class FSStore:
    ''' Class for storing and retriving records as pickle files.
    Useful in multi-threading applications where a direct database
        insertion for each process would cause too much blocking.
    '''
    default_settings = {
        'readonly': False,
    }
    def __init__(self, folder, records=None, save_every=10000, 
                seed_range=100000000, check_collision=True, 
                settings_fname='.settings_FSStore.json'):

        self.save_every = save_every
        self.folder = folder
        self.check_collision = check_collision
        self.seed_range = seed_range
        self.settings_fname = f'{folder}/{settings_fname}'

        # intial settings
        self.set_seed()
        self.ct = 0

        # keep initial records data
        if records is not None:
            self.records = list(records)
        else:
            self.records = list()

        self.init_folder()

    def __del__(self):
        ''' Save buffer before being deleted.
        '''
        self.dump_file()
        

    
    ########################### Manage state ###########################
    def init_folder(self):
        # make folder if it does not exist
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)
        
        # write defaulted settings file
        self.write_settings()

    def set_seed(self):
        ''' Set random seeds for filename purposes.
        '''
        # (2x bc lower probability of collision)
        self.seed = random.randrange(self.seed_range/10, self.seed_range)
        self.seed += random.randrange(self.seed_range/10, self.seed_range)

    ########################### Work with Settings File ###########################

    def check_readonly(self):
        ''' Raise exception if system set to readonly.
        '''
        if self.read_settings().get('readonly', False):
            raise PermissionError('FSStore has set the parameter readonly=True. '
                f'To change, use .write_settings(readonly=False)')

    def read_setting(self, name):
        ''' Read file and return value of a particular setting.
        '''
        return self.read_settings()[name]

    def read_settings(self):
        ''' Read settings file.
        '''
        if os.path.exists(self.settings_fname):
            return read_json(self.settings_fname)
        else:
            return dict()

    def write_settings(self, **newsettings):
        ''' Read settings file and update any missing values.
        '''
        if not all([k in self.default_settings for k in newsettings.keys()]):
            raise KeyError(f'Invalid setting in {set(newsettings.keys())} provided to '
                f'.write_settings(). Should be one of {set(self.default_settings.keys())}')
        settings = {**self.default_settings, **self.read_settings(), **newsettings}
        write_json(settings, self.settings_fname)

    def clear_settings(self):
        ''' Replace settings to defaults.
        '''
        write_json(self.default_settings, self.settings_fname)

    ########################### Writing data ###########################
    def insert(self, record):
        ''' Add a single record.
        '''
        self.check_readonly() # raise exception if set to readonly

        self.records.append(record)
        self.ct += 1

        if self.ct % self.save_every == 0:
            self.dump_file()

    def dump_file(self):
        ''' Save records to file and empty container.
        '''
        self.check_readonly() # raise exception if set to readonly

        if len(self.records):
            fname = self.get_fname()
            if self.check_collision and os.path.exists(fname):
                raise FileExistsError(f'There was a collision in FSStore '
                            f'with seed={self.seed}, count={self.ct}, fname={fname}')
            
            write_pickle(self.records, fname)
        self.records = list()

    def get_fname(self):
        return f'{self.folder}/{self.seed+self.ct}.pic'

    
    
    ########################### Reading data ###########################
    def get_exist_fnames(self):
        return glob.glob(f'{self.folder}/*.pic')

    def select_chunks(self, loadbar=False):
        ''' Yield records in file-sized chunks.
        '''
        fnames = self.get_exist_fnames()
        if loadbar:
            fnames = tqdm(fnames)
        
        for fname in fnames:
            yield read_pickle(fname)
    
    def yield_records(self, **kwargs):
        ''' Reads pickle records and yields them one at a time.
        '''
        for records in self.select_chunks(**kwargs):
            for rec in records:
                yield rec
    
    def select_records(self, **kwargs):
        ''' Creates list of records from .yield_records()
        '''
        return list(self.yield_records(**kwargs))



    ########################### Deleting data ###########################
    def delete_records(self, force=False):
        ''' Delete records (NOT settings or folder).
        '''
        if not force:
            self.check_readonly() # raise exception if set to readonly

        for fname in self.get_exist_fnames():
            os.remove(fname)

    def delete_all_completely(self, force=False):
        ''' Will delete all records and the containing directory.
        '''
        if not force:
            self.check_readonly() # raise exception if set to readonly
        
        for fname in glob.glob(f'{self.folder}/*') + glob.glob(f'{self.folder}/.*'):
            os.remove(fname)
        os.rmdir(self.folder)
















