import sys
sys.path.append('..')
import doctable

def test_basic():

    timer = doctable.Timer('starting tests')

    timer.step('init fsstore')
    fs = doctable.FSStore('tmp', save_every=100)
    
    # test resetting of seed
    seed1 = fs.seed
    fs.set_seed()
    assert(seed1 != fs.seed)

    timer.step(f'deleting old records')
    fs.delete_all()

    timer.step(f'seed={fs.seed}; inserting records')

    records = [i for i in range(1000)]
    for r in records:
        fs.insert(r)

    fs.dump_file()

    timer.step('finished inserting; now checking integrity')
    assert(sum(records) == sum(fs.read_all_records()))

    timer.step('assertion passed!')


if __name__ == '__main__':
    test_basic()
