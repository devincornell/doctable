import torch
import numpy as np

import sys
sys.path.append('..')
import doctable

@doctable.schema
class Sample:
    __slots__ = []
    id: int
    vec: torch.Tensor


if __name__ == '__main__':  
    #device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    #device = torch.device('cuda:0')
    device = torch.device('cpu')
    print(device)
    timer = doctable.Timer()

    if True:
        timer.step('creating matrix')
        nsamp = int(100e3)
        V = torch.rand((nsamp, 300)).to(device)
        
        timer.step('creating objects to encapsulate')
        samps = list()
        for i in range(V.shape[0]):
            samps.append(Sample(i, V[i,:]))

        a_vec = torch.rand((300)).to(device)
        a_mat = torch.rand((10000, 300)).to(device)
        
        timer.step('executing single vectors')
        def testfunc():
            for s in samps:
                a_mat.mv(s.vec)

        print(doctable.Timer.time_call(testfunc, as_str=True, num_calls=10))


    if False:
        timer.step('making numpy matrices')
        nsamp = 1000000
        np_mat = np.random.rand(nsamp, 300)
        np_vec = np.random.rand(300)

        timer.step('making pytorch matrices')
        rand_tensor = torch.rand((nsamp, 300))
        rand_vec = torch.rand((300,))

        timer.step('making gpu matrices')
        gpu_tensor = rand_tensor.to(device)
        gpu_vec = rand_vec.to(device)

        timer.step('calling functions')
        print(doctable.Timer.time_call(lambda: np_mat.dot(np_vec), as_str=True, num_calls=100))
        print(doctable.Timer.time_call(lambda: rand_tensor.mv(rand_vec), as_str=True, num_calls=100))
        print(doctable.Timer.time_call(lambda: gpu_tensor.mv(gpu_vec), as_str=True, num_calls=100))

