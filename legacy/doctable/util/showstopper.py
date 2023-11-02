
from multiprocessing import Pool


def showstopper(n_cores=12, n=100000):
    ''' Totally fills a machine's resources until you can kill it.
    '''
    with Pool(n_cores) as p:
        p.map(malloc_thread, list(range(n)))

def malloc_thread(i, k=10000000):
    stuff = list()
    while True:
        try:
            stuff.append(list(range(k)))
        except:
            print('.', end='')


