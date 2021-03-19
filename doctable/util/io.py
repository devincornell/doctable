
import pickle
import json

def read_pickle(fname, verbose=False):
    if verbose: print(f'Reading pickle {fname}')
    with open(fname, 'rb') as f:
        return pickle.load(f)

def write_pickle(obj, fname, verbose=False):
    if verbose: print(f'Writing pickle {fname}')
    with open(fname, 'wb') as f:
        pickle.dump(obj, f)

def read_json(fname, verbose=False):
    if verbose: print(f'Reading json {fname}')
    with open(fname, 'r') as f:
        return json.load(f)

def write_json(obj, fname, verbose=False):
    if verbose: print(f'Writing json {fname}')
    with open(fname, 'w') as f:
        json.dump(obj, f)

