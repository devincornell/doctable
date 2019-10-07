from sklearn.datasets import fetch_20newsgroups
import pandas as pd


def get_sklearn_newsgroups(useN = None):
    news_data = fetch_20newsgroups(shuffle=True, random_state=0)

    fnames = [fn.split('/')[-1] for fn in news_data['filenames']]
    target_names = [news_data['target_names'][t] for t in news_data['target']]
    texts = news_data['data']
    df = pd.DataFrame({'filename':fnames[:useN], 'target':target_names[:useN], 'text':texts[:useN]})
    return df

