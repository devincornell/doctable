import pickle
import pathlib
import spacy



import sys
sys.path.append('..')
import doctable
import timing

import tqdm
import urllib.request
def download_nss(
	baseurl='https://raw.githubusercontent.com/devincornell/nssdocs/master/docs/',
	years = (1987, 1988, 1990, 1991, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2002, 2006, 2010, 2015, 2017)
	):
	def read_url(url):
		return urllib.request.urlopen(url).read().decode('utf-8')
	
	ftemp = baseurl+'{}.txt'
	all_texts = [read_url(ftemp.format(year)) for year in tqdm.tqdm(years)]
	return {yr:text for yr,text in zip(years,all_texts)}

def write_trees_pickle(ptrees, fpaths, use_dict=True):
    for fpath, ptree in zip(fpaths, ptrees):
        if use_dict:
            fpath.write_bytes(ptree.as_pickle())
        else:
            fpath.write_bytes(pickle.dumps(ptree))

def av_file_size(fpaths):
    sizes = list()
    for fpath in fpaths:
        sizes.append(fpath.stat().st_size)
    return sum(sizes) / len(sizes)

def read_trees_pickle(fpaths, use_dict=True):
    trees = list()
    for fpath in fpaths:
        if use_dict:
            trees.append(doctable.ParseTree.from_pickle(fpath.read_bytes()))
        else:
            trees.append(pickle.loads(fpath.read_bytes()))
    return trees

if __name__ == '__main__':
    cache_path = pathlib.Path('tmp_nss/nss_data.pic')
    timer = doctable.Timer()

    if not cache_path.exists():
        timer.step('Downloading nss files.')
        nss_texts = download_nss()

        timer.step('parsing files')
        nlp = spacy.load('en_core_web_sm')
        docs = [nlp(text) for yr,text in tqdm.tqdm(nss_texts.items())]
        
        # saving for future use
        cache_path.write_bytes(pickle.dumps(docs))
    else:
        timer.step('cache file found - now reading')
        docs = pickle.loads(cache_path.read_bytes())

    timer.step('create list of parsetrees')
    trees = [doctable.ParseTree.from_spacy(sent) for doc in docs for sent in doc.sents]
    print(trees[2])

    timer.step('creating file paths')
    tmp = doctable.TempFolder('tmp_parsetrees')
    fpaths = [tmp.path/f'{i}.pic' for i in range(len(trees))]
    
    timer.step('testing dictionary-based method')
    f = lambda: write_trees_pickle(trees, fpaths, use_dict=True)
    print(f'dict-based write: {timing.time_call(f)}')
    print(f'av filesize: {av_file_size(fpaths)/1000:0.2f} kB')
    f = lambda: read_trees_pickle(fpaths, use_dict=True)
    print(f'dict-based read: {timing.time_call(f)}')

    timer.step('cleaning up files')
    for fpath in fpaths:
        fpath.unlink()

    timer.step('testing raw pickle method')
    f = lambda: write_trees_pickle(trees, fpaths, use_dict=False)
    print(f'pickle-based write: {timing.time_call(f)}')
    print(f'av filesize: {av_file_size(fpaths)/1000:0.2f} kB')
    f = lambda: read_trees_pickle(fpaths, use_dict=False)
    print(f'pickle-based read: {timing.time_call(f)}')
    


