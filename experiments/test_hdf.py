
import h5py
import numpy as np

import sys
sys.path.append('..')
import doctable

if __name__ == '__main__':
    
    stepper = doctable.Stepper()
    
    with h5py.File('tmp.hdf5', 'w') as f:
        print(list(f.keys()))
        dset = f.create_dataset("myd", shape=(5,))
        
        binary_blob = b"Hello\x00Hello\x00"
        
        for i in stepper.tqdm(range(10000)):
            dset.attrs[f"attr_{i}"] = np.void(binary_blob)
        
        print(dset.attrs["attr_0"].tobytes())

