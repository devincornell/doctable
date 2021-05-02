import time
import datetime
import auth
import firebasedata_monitor as firebasedata
import gdrive
import os.path
import pandas as pd


def save_userdata(userdata, base_fname):
    
    # convert to dataframe
    df = pd.DataFrame(userdata)
    
    # mark if someone is matched or not
    df['is_matched'] = ~df['chatID'].isna()
    df.loc[df['postComplete'].isna(), 'postComplete'] = False
    df.loc[df['canMessage'].isna(), 'canMessage'] = False
    df.loc[df['preComplete'].isna(), 'preComplete'] = False
    
    # sort columns alphabetically to group preSurvey/postSurvey Q.
    # sort rows by log in time
    df = df.reindex(sorted(df.columns), axis=1)
    df = df[df['runID'] == 'yougov2']
    df = df.sort_values(['logInTime'], ascending=False)
    
    # add in hour for easy summary stats
    sel = ~df['logInTime'].isna()
    df['hr'] = None
    df.loc[sel, 'hr'] = df.loc[sel, 'logInTime']\
            .map(lambda x: '{:0>2}/{}-{:0>2}hrs'.format(x.month, x.day, x.hour))
    
    
    # save csv
    csv_fname = base_fname + '.csv'
    df.to_csv(csv_fname, index=False)
    
    # save picle file
    pic_fname = base_fname + '.pic'
    df.to_pickle(pic_fname)
    
    # return filenames for uploading to google drive
    return df, csv_fname, pic_fname


def save_chatdata(chatdata, base_fname):
    #print(chatdata)
    df = pd.DataFrame(chatdata)

    # save csv
    csv_fname = base_fname + '.csv'
    df.to_csv(csv_fname, index=False)
    
    # save picle file
    pic_fname = base_fname + '.pic'
    df.to_pickle(pic_fname)
    
    #n_chats = len(set([c['chatID'] for c in chatdata]))
    #print('\nsaved {} messages from {} chats to {}.'.format(len(chatdata), n_chats, chatfname))
    return df, csv_fname, pic_fname


if __name__ == '__main__':
    
    period_min = 180
    
    fb = firebasedata.authenticate()
    
    while True:
        
        # authenticate for firebase
        gservice = gdrive.authenticate()
        
        # filenames
        datestr = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M')
        basefname = datestr
        data_dump_folder = 'data_dumps'
        log_report_folder = 'log_reports'
        
        # download user data
        userdata = firebasedata.download_userdata(fb, verbose=True)
        fpath = os.path.join(data_dump_folder,basefname+'_users')
        udf, ucsv, upic = save_userdata(userdata, fpath)
        
        # upload user data
        print(gdrive.upload(gservice, ucsv, data_dump_folder))
        print(gdrive.upload(gservice, upic, data_dump_folder))
        print('uploaded user files!')
        
        # make log report
        logfname = make_report(log_report_folder, udf, datestr, fb)
        print(gdrive.upload(gservice, logfname, log_report_folder))        
        print('uploaded log files')
        
        # download chat data
        users = list(udf['code'])
        chatdata = firebasedata.download_chatdata(fb, users, verbose=True)
        fpath = os.path.join(data_dump_folder,basefname+'_chats')
        cdf, ccsv, cpic = save_chatdata(chatdata, fpath)
        
        # upload all files
        print(gdrive.upload(gservice, ccsv, data_dump_folder))
        print(gdrive.upload(gservice, cpic, data_dump_folder))
        print('uploaded chat files!')
        
        print('destroying connections')
        #del fb
        del gservice
        
        # wait for some time
        print(f'sleeping for {period_min} minutes.')
        sleep = period_min*60
        time.sleep(sleep)
    