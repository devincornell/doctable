
from typing import List
from dataclasses import dataclass, field
import pytest
import os
import glob
import itertools
import copy

import sys
sys.path.append('..')
import doctable

import pathlib
import shutil



def test_tempfolder():
    folder = 'tmp'
    p = pathlib.Path(folder)
    if os.path.exists(p):
        shutil.rmtree(p)

    with doctable.TempFolder(p):
        assert(os.path.exists(p))
    assert(not os.path.exists(p))

    tmp = doctable.TempFolder(p, make_folder=True)
    with open(tmp.joinpath('file.txt'), 'w') as f:
        f.write('')
    assert(len(tmp.rglob('*.txt'))==1)
    tmp.rmtree()
    assert(not os.path.exists(tmp.path))

    tmp = doctable.TempFolder(p, make_folder=True)
    assert(not os.path.exists(tmp.path))
    tmp.mkdir()
    assert(os.path.exists(tmp.path))
    tmp.rmtree()
    assert(not os.path.exists(tmp.path))


if __name__ == '__main__':
    test_tempfolder()
