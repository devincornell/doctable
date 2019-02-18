
from example_newsarticles import NewsArticles
from glob import glob
from datetime import datetime
import string


if __name__ == '__main__':
    
    newsarticles = NewsArticles('testarticles.db')
    
    for fname in glob('sampletexts/*.txt'):
        rowdata = dict() # populate with document fields
        
        # parses fname into components
        src, docname, datestr = '_'.join(fname.split('/')[-1].split('.')[:-1]).split('_')
        
        # conver date string to datetime
        month, day, year = datestr.split('-')
        dateobj = datetime(month=int(month), day=int(day), year=int(year))
        
        # follows database schema: id integer primary key autoincrement, newssource string, docname string, timestamp int, datestr string, fname string, text string, bow blob
        rowdata['newssource'] = src
        rowdata['docname'] = docname
        rowdata['timestamp'] = dateobj.timestamp()
        rowdata['datestr'] = dateobj.strftime("%Y/%m/%d")
        rowdata['fname'] = fname
        
        with open(fname,'r') as f:
            text = f.read()
        rowdata['text'] = text
        
        #bowstr = text.translate(None, string.punctuation)
        translator = str.maketrans('', '', string.punctuation)
        bowstr = text.translate(translator)
        rowdata['bow'] = bowstr.split()
        
        # adding a single row at a time (see ifnotunique parameter)
        newsarticles.add(rowdata, ifnotunique='REPLACE')
        
        
    print('Printing added data as dataframe:')
    print(newsarticles.getdf()[['newssource','docname','datestr']])
    print()
    
    print('Printing one row at a time:')
    for art in newsarticles.get():
        print(art['newssource'], art['docname'], art['datestr'], 'has', len(art['bow']), 'words.')
    print()
    
    exit()
    
    # add easytext pipeline component to new spacy parser
    nlp = spacy.load('en')
    #et = EasyTextPipeline()
    #nlp.add_pipe(et, last=True)
    


    #t1 = 'Today I ran over the log with my car in the United States of America. The U.S. went to the store. I went to the hat.'
    #t2 = 'The United States said they wouldnt get involved. Russia attacked Canada.'
    #texts = [t1,t2]
    
    with open('sampletexts/test.txt','r') as f:
        text = f.read()
    texts = [l for l in text.split('\n') if len(l) > 0]
    names = list(range(len(texts)))
    print(len(texts), 'texts found.')
    
    docs = list(nlp.pipe(texts))
    
    entlist, entmap = extract_entities(docs)
    print(entlist)
    print()
    
    preps = extract_prepositions(docs)
    print(preps)
    print()
    
    nv = extract_nounverbs(docs)
    print(nv)
    print()
    
    ev = extract_entverbs(docs)
    print(ev)
    print()
    
        
    #entdf = dict2df(entcts, names)
    #entdf.append(count_totals(entcts))
    
    #prepdf = dict2df(prepcts, names)
    #nvdf = dict2df(nvcts, names)
    #evdf = dict2df(evcts, names)
    #print(entdf)

