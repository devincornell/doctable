
import numpy as np
import cupy as cp
import doctable

if __name__ == '__main__':

    timer = doctable.Timer()

    ### Numpy and CPU
    timer.step('making numpy array')
    X_cpu = np.random.rand(2500000, 300)
    y_cpu = np.random.rand(300)
    
    timer.step('transferring to gpu')
    X_gpu = cp.asarray(X_cpu)
    y_gpu = cp.asarray(y_cpu)

    x0 = X_gpu[0,:]
    print(x0.shape, type(x0))

    timer.step('multiplying on gpu')
    result = X_gpu.dot(y_gpu)
    cp.cuda.Stream.null.synchronize()
    timer.step('finished.')
    print(result.shape, type(result))

    timer.step('multiplying on cpu')
    result = X_cpu.dot(y_cpu)
    timer.step('finished.')
    print(result.shape, type(result))

    #timer.step('finish gpu array')
    
