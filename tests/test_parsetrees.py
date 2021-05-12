
import pytest

import spacy

import sys
sys.path.append('..')
import doctable

ex_sents = '''
This is the best day ever, honestly. 
I am having a ton of fun with you. 
Programming is awesome!
'''.replace('\n','')

def test_basic():
    nlp = spacy.load('en_core_web_sm', disable=['ner'])
    tmp = doctable.TempFolder('tmp')

    # verify operation by pickling/dicting and undicting
    trees = list()
    for sent in nlp(ex_sents).sents:
        
        tree = doctable.ParseTree.from_spacy(sent)
        trees.append(tree)
        print(sent)
        print(tree)
        
        assert(len(tree) == len(sent))

        fname = 'test_tree.pic'
        with tmp.path.joinpath(fname).open('wb') as f:
            f.write(tree.as_pickle())

        with tmp.path.joinpath(fname).open('rb') as f:
            othertree = doctable.ParseTree.from_pickle(f.read())

        assert(repr(tree) == repr(othertree))

    # now work with single tree
    tree = trees[0]
    assert(tree.root.text == 'is')
    assert(tree.root.tag == 'VBZ')

    # recall that ner was disabled
    with pytest.raises(doctable.parse.token.PropertyNotAvailable):
        tree.root.ent == ''
    

if __name__ == '__main__':
    test_basic()
    
    