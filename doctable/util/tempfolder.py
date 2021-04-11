

import os
import shutil
import pathlib
#import dataclasses

#@dataclasses.dataclass
class TempFolder:
    def __init__(self, folder: str, make_folder:bool=True):
        self.path = pathlib.Path(folder)

        if make_folder:
            self.mkdir()

    def mkdir(self):
        ''' Make the directory if it does not exist.
        '''
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def rmtree(self, **kwargs):
        ''' Remove all files recursively in the folder.
        '''
        if os.path.exists(self.path):
            shutil.rmtree(self.path, **kwargs)
    
    def rglob(self, p='*', **kwargs):
        ''' Get list of filenames in the directory.
        '''
        return list(self.path.rglob(p, **kwargs))

    def joinpath(self, fname):
        ''' Join path with provided fname.
        '''
        return self.path.joinpath(fname)
    
    def __del__(self):
        ''' Delete the directory.
        '''
        self.rmtree()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rmtree()






