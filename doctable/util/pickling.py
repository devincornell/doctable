
import pickle

def read_pickle(fname, verbose=False):
    if verbose: print(f'Reading pickle {fname}')
    with open(fname, 'rb') as f:
        return pickle.load(f)

def write_pickle(obj, fname, verbose=False):
    if verbose: print(f'Writing pickle {fname}')
    with open(fname, 'wb') as f:
        pickle.dump(obj, f)
