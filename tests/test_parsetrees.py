
import pytest

import sys
sys.path.append('..')
import doctable

ex_parsetree = {'i': 1,
 'text': 'went',
 'tag': 'VBD',
 'dep': 'ROOT',
 'info': {'random': None},
 'childs': [{'i': 0,
   'text': 'I',
   'tag': 'PRP',
   'dep': 'nsubj',
   'info': {},
   'childs': [],
   'pos': 'PRON',
   'ent': ''},
  {'i': 2,
   'text': 'to',
   'tag': 'IN',
   'dep': 'prep',
   'info': {},
   'childs': [{'i': 4,
     'text': 'store',
     'tag': 'NN',
     'dep': 'pobj',
     'info': {},
     'childs': [{'i': 3,
       'text': 'the',
       'tag': 'DT',
       'dep': 'det',
       'info': {},
       'childs': [],
       'pos': 'DET',
       'ent': ''}],
     'pos': 'NOUN',
     'ent': ''}],
   'pos': 'ADP',
   'ent': ''},
  {'i': 5,
   'text': 'today',
   'tag': 'NN',
   'dep': 'npadvmod',
   'info': {},
   'childs': [],
   'pos': 'NOUN',
   'ent': 'DATE'},
  {'i': 6,
   'text': '.',
   'tag': '.',
   'dep': 'punct',
   'info': {},
   'childs': [],
   'pos': 'PUNCT',
   'ent': ''}],
 'pos': 'VERB',
 'ent': ''}



def test_basic():
    tok = doctable.Token(ex_parsetree)
    assert(tok.t == 'went')
    assert(len(tok.childs) == 4)
    assert(tok.i == 1)
    assert(tok['random'] is None)
    

    assert(len(tok.get_childs({'whatever'})) == 0)
    assert(len(tok.get_childs({'nsubj'})) == 1)

    assert(tok.get_child({'nsubj'}).t == 'I')
    assert(tok.get_child({'whatever'}, first=True).is_none)
    
    assert(not tok.get_child({'nsubj','prep'}, first=True).is_none)
    with pytest.raises(ValueError):
        tok.get_child({'nsubj','prep'})
    

if __name__ == '__main__':
    test_basic()
    
    