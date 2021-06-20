
import torch
from tqdm import tqdm

import sys
sys.path.append('..')
import doctable



if __name__ == '__main__':  
    device = torch.device('cuda:0')
    #device = torch.device('cpu')

    # TASK: find sims between all points in this space
    shape = (int(2.5e6), 300)
    X = torch.rand(shape).to(device)
    X = X / X.norm(p=2, dim=1)[:,None] # row-normalize
    #print(X.norm(p=2, dim=1))

    sims = torch.zeros((X.shape[0],))
    for s in tqdm(doctable.chunk_slice(X.shape[0], chunk_size=100)):
        sims[s] = X.matmul(X[s,:].T).T.mean(1)

    print((sims==0).sum())
        



