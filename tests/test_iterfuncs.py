import random
import dataclasses
import pprint

import sys
sys.path.append('..')
#from doctable import DocTable2, func, op
import doctable

@dataclasses.dataclass
class Element:
    a: str
    b: int
    c: int


def test_groupby():
    
    elements = [Element(f'name_{i//3}', i, i*10) for i in range(10)]

    groups = doctable.groupby(elements, keys=[lambda e: e.a])
    pprint.pprint(groups)
    assert(len(groups)==4)
    pprint.pprint(groups.flatten())
    pprint.pprint(groups.ungroup())

        
    groups = doctable.groupby(elements, keys=[lambda e: e.a, lambda e: e.b % 2, lambda e: e.c//20])
    pprint.pprint(groups)
    assert(len(groups) == 4)
    assert(len(groups['name_0']) == 2)
    pprint.pprint(groups.flatten())
    pprint.pprint(groups.ungroup())
    
    keys = [lambda e: e.a, lambda e: e.b % 2, lambda e: e.c//20]
    groups = doctable.GroupedData.group_elements(elements, keys=keys)
    pprint.pprint(groups)
    assert(len(groups)==4)
    pprint.pprint(groups.ungroup())
    pprint.pprint(groups.flatten())


if __name__ == '__main__':
    test_groupby()

    


