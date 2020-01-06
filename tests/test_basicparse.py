

def chunk_parse(cls, text, nlp, parsefuncs, preprocessfunc=None, paragraph_sep=None, max_sent=10):
    '''Parses a single document by breaking it into chunks for lower memory consumption.
    '''
    # split into paragraphs (or simulate)
    if paragraph_sep is not None:
        texts = [par.strip() for par in text.split(paragraph_sep) if len(par.strip()) > 0]
        text_chunks = [cls._split_texts(par, max_sent) for par in texts]
    else:
        text_chunks = [cls._split_texts(text, max_sent)]
    
    par_dat = list()
    for par in pars:
        chunk_dat = list()
        for tchunk in text_chunks:
            doc = nlp(tchunk)
            chunk_dat.append([pfunc(doc) for pfunc in parsefuncs])
            del doc
        par_dat.append(list(zip(*chunk_dat)))
    print('par_dat')
        
def _split_texts(cls, text, max_sent):
    sents = re.split('[\?\!\.]', text)

def test_parsebreaker()
    texts_small = ['The hat is red. And so are you.\n\nWhatever, they said. Whatever indeed.', 
               'But why is the hat blue?\n\nAre you colorblind? See the answer here: http://google.com']
