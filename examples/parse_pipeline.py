import sys
sys.path.append('..')
import doctable as dt
import spacy

print(dir(dt.docparser))

if __name__ == '__main__':
    
    nlp = spacy.load('en')
    
    pipeline = dt.parse.Pipeline([
        lambda text: dt.parse.preprocess(text, replace_xml=''),
        
        nlp, # spacy nlp parser object
        
        lambda doc: dt.parse.merge_tok_spans(doc, merge_ents=True),
        
        lambda doc: dt.parse.tokenize(doc,
            split_sents=True,
                                      
            filter_tok_func = lambda tok: dt.parse.filter_tok(tok,
                punct=True,
                stop=True, # filter stopwords and punctuation
            ),
            
            parse_tok_func = lambda tok: dt.parse.parse_tok(tok,
                digit_replacement = 'XXXNUMXXX',
            )
        ),
    ])
    
    
    texts = [
            'Hello world! Happy birthday. What do you want to do today? Maybe go to the store?',
            'I wish you would tell me when you\'re going to the store. I might have asked you to get some milk?'
           ]
    
    tokens = pipeline.parse(texts[0])
    print(tokens)
    
    tokens = pipeline.parsemany(texts)
    print(tokens)
    
    #tokens = p.parse('Hello! How are you doing Donald Trump?')
    #print(tokens)
    

