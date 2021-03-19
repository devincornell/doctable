import sys
sys.path.append('..')
import doctable

if __name__ == '__main__':

    timer = doctable.Timer('starting tests')

    timer.step('init fsstore')
    fs = doctable.FSStore('tmp', save_every=100)

    timer.step(f'deleting old records')
    fs.delete_all()

    timer.step(f'seed={fs.seed}; inserting records')

    records = [i for i in range(10000)]
    for r in records:
        fs.insert(r)

    fs.dump_file()

    timer.step('finished inserting; now checking integrity')
    assert(sum(records) == sum(fs.read_all_records()))

    timer.step('assertion passed!')
