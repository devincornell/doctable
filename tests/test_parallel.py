
import sys
sys.path.append('..')
import doctable

if __name__ == '__main__':
    data = range(100)

    # create pool and pipes
    with doctable.AsyncDistribute(2) as d:
        results = d.map(lambda x: x, data)
    
    print(len(results))
    print('waiting on processes')


