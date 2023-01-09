
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

def test_parsetreedocs():
    nlp = spacy.load('en_core_web_sm', disable=['ner'])
    import tempfile
    tempdir = tempfile.TemporaryDirectory()
    tmp = tempdir.name

    spacydoc = nlp(ex_sents)
    doc = doctable.ParseTreeDoc.from_spacy(spacydoc)
    doc_dict = doc.as_dict()
    new_doc = doctable.ParseTreeDoc.from_dict(doc_dict)
    
    #print(doc[0])
    #print(len(doc), len(list(spacydoc.sents)))
    assert(len(list(doc.tokens)) == len(list(spacydoc)))
    assert(len(doc) == len(list(spacydoc.sents)))
    assert(repr(doc) == repr(new_doc))

    for sent, new_sent in zip(doc, new_doc):
        
        assert(repr(sent) == repr(new_sent))

        # recall that ner was disabled
        with pytest.raises(doctable.textmodels.PropertyNotAvailable):
            sent.root.ent == ''

        # recall that ner was disabled
        with pytest.raises(doctable.textmodels.PropertyNotAvailable):
            new_sent.root.ent == ''

if __name__ == '__main__':
    test_parsetreedocs()
    
    