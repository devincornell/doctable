import os
import pytest
from random import randrange


import sys
sys.path.append('..')
from doctable import DocTable


def test_init():
    consts = ('UNIQUE(id)',)
    dt = DocTable(('id integer', 'junk blob'), fname='dude.db',constraints=consts)
    print(dt)


if __name__ == '__main__':
    test_init()
    #test_add_many()

