import torch
import numpy as np

import sys
sys.path.append('..')
import doctable

@doctable.row
class Sample:
    




if __name__ == '__main__':  
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(device)
    timer = doctable.Timer()

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

