
import sys
sys.path.append('..')
import doctable

class MySequence(list):
    def sum(self):
        return sum(self)


def test_result_containers():
    t = doctable.Timer()

    t.step('constructing from range')
    seq = MySequence(range(10))
    t.step('')
    print(seq.sum())


if __name__ == '__main__':
    test_result_containers()

