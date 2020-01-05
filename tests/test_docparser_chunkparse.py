
import sys
sys.path.append('..')
import doctable
import spacy
from pprint import pprint

def test_chunkparse():
    texts = ['The hat is red. And so are you.\n\nWhatever, they said. Whatever indeed. Whell, in any case, who cares?', 
               'But why is the hat blue?\n\nAre you colorblind? '
                   'See the answer here: http://google.com']
    nlp = spacy.load('en')
    
    parse_funcs = {
        'doc': lambda doc: doc, 
        #'toks': lambda doc: ' '.join(t.lower_ for t in doc)
    }
    
    for text in texts:
        #print('starting')
        parsed = doctable.DocParser.parse_text_chunks(text, nlp, parse_funcs=parse_funcs,
                paragraph_sep='\n\n', chunk_sents=1)
        pprint(parsed)
        print('----------------------------------')

if __name__ == '__main__':
    test_chunkparse()
    
    