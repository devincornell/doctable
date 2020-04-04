import urllib.request
import spacy
import doctable

nss_metadata = {
    1987: {'party': 'R', 'president': 'Reagan'}, 
    1993: {'party': 'R', 'president': 'H.W. Bush'}, 
    2002: {'party': 'R', 'president': 'W. Bush'}, 
    2015: {'party': 'D', 'president': 'Obama'}, 
    1994: {'party': 'D', 'president': 'Clinton'}, 
    1990: {'party': 'R', 'president': 'H.W. Bush'}, 
    1991: {'party': 'R', 'president': 'H.W. Bush'}, 
    2006: {'party': 'R', 'president': 'W. Bush'}, 
    1997: {'party': 'D', 'president': 'Clinton'}, 
    1995: {'party': 'D', 'president': 'Clinton'}, 
    1988: {'party': 'R', 'president': 'Reagan'}, 
    2017: {'party': 'R', 'president': 'Trump'}, 
    1996: {'party': 'D', 'president': 'Clinton'}, 
    2010: {'party': 'D', 'president': 'Obama'}, 
    1999: {'party': 'D', 'president': 'Clinton'}, 
    1998: {'party': 'D', 'president': 'Clinton'}, 
    2000: {'party': 'D', 'president': 'Clinton'}
}

def download_nss(
	baseurl='https://raw.githubusercontent.com/devincornell/nssdocs/master/docs/',
	years = (1987, 1988, 1990, 1991, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2002, 2006, 2010, 2015, 2017)
	):
	def read_url(url):
		return urllib.request.urlopen(url).read().decode('utf-8')
	
	ftemp = baseurl+'{}.txt'
	all_texts = [read_url(ftemp.format(year)) for year in years]
	return {yr:text for yr,text in zip(years,all_texts)}

def download_all_nssdata():
    nss_texts = download_nss()
    all_nss = {yr: {**md, 'text': nss_texts[yr], 'year':yr} 
               for yr,md in nss_metadata.items()}
    years = list(sorted(all_nss.keys()))
    list_nss = [all_nss[yr] for yr in years]
    
    return list_nss
        


class NSSParser:
    ''' Handles text parsing for NSS documents.'''
    def __init__(self):
        nlp = spacy.load('en')
        
        # this determines all settings for tokenizing
        self.pipeline = doctable.ParsePipeline([
            nlp, # first run spacy parser
            doctable.component('merge_tok_spans', merge_ents=True),
            doctable.component('tokenize', **{
                'split_sents': False,
                'keep_tok_func': doctable.component('keep_tok'),
                'parse_tok_func': doctable.component('parse_tok', **{
                    'format_ents': True,
                    'num_replacement': 'NUM',
                })
            })
        ])
        
    def parse(self, text):
        return self.pipeline.parse(text)
    
    def parsemany(self, texts, workers=1):
        return self.pipeline.parsemany(texts, workers=workers)

parser = NSSParser() # creates a parser instance
parser.pipeline.components





