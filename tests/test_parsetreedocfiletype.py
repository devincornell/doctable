
import pytest

import spacy
import dataclasses

import sys
sys.path.append('..')
import doctable

ex_sents = '''
This is the best day ever, honestly. 
I am having a ton of fun with you. 
Programming is awesome!
'''.split('\n')

@dataclasses.dataclass
class TestRow(doctable.DocTableRow):
    id: int = doctable.IDCol()
    doc: doctable.ParseTreeDoc = doctable.Col(type_args=dict(folder='tmp/parsed_trees'))

def test_parsetreedocs():
    nlp = spacy.load('en_core_web_sm', disable=['ner'])
    tmp = doctable.TempFolder('tmp')
    db = doctable.DocTable(schema=TestRow, target=':memory:')

    spacydocs = [nlp(t) for t in ex_sents]
    docs = [doctable.ParseTreeDoc.from_spacy(sd) for sd in spacydocs]
    db.insert([{'doc':doc} for doc in docs])
    
    # select the documents back
    sdocs = [r['doc'] for r in db.select()]
    assert(isinstance(sdocs[0], doctable.ParseTreeDoc))

    for doc, new_doc in zip(docs, sdocs):
        print(repr(doc))
        assert(repr(doc) == repr(new_doc))

        for sent, new_sent in zip(doc, new_doc):
            
            assert(repr(sent) == repr(new_sent))

            # recall that ner was disabled
            with pytest.raises(doctable.parse.token.PropertyNotAvailable):
                sent.root.ent == ''

            # recall that ner was disabled
            with pytest.raises(doctable.parse.token.PropertyNotAvailable):
                new_sent.root.ent == ''

if __name__ == '__main__':
    test_parsetreedocs()
    
    