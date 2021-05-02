


#  pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
#   pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

from __future__ import print_function
import pickle
import os.path
import pathlib

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from googleapiclient.http import MediaFileUpload



class Drive:
    default_scopes = [
        #'https://www.googleapis.com/auth/drive.metadata.readonly',
        'https://www.googleapis.com/auth/drive',
         ]
    def __init__(self, cache_fname='credentials/gdrive-loginsave.pickle', 
                cred_fname='credentials/gdrive-credentials.json', scopes=None)

        self.scopes = scopes if scopes is not None else default_scopes
        self.cache_path = pathlib.Path(cache_fname)
        self.cred_path = pathlib.Path(cred_fname)
        self.creds = self.read_creds()
        self.service = None

    def read_creds(self):
        if self.cache_path.exists():
            with self.cache_path.open('rb') as f:
                creds = pickle.load(f)
                return creds
        else:
            return None
    
    def write_creds(self, creds):
        self.cache_path.mkdir(parents=True, exist_ok=True)
        with self.cache_path.open('wb') as f:
            pickle.dump(creds, f)
        
    def authenticate(self):
        '''Authenticate the application and save service and credentials.
        '''
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                                            cred_fname, SCOPES)
                #creds = flow.run_local_server(port=0)
                self.creds = flow.run_console()
            
            # Save the credentials for the next run
            self.write_creds(self.creds)

        self.service = build('drive', 'v3', credentials=self.creds)

    def upload_file(self, fname, target_id):
            
        if isinstance(target_id, str):
            target_id = [target_id]

        media = MediaFileUpload(fname, mimetype=self.mimetype_lookup(fname))
        
        # prepare metadata
        file_metadata = {
            'name': os.path.basename(fname), 
            'parents': target_id,
        }

        # may throw BrokenPipeError! IDK HOW TO FIX
        file = service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()
        return file
            
    def mimetype_lookup(self, fname):
        if fname.endswith('.csv'):
            mimetype = 'text/csv'
        elif fname.endswith('.pic'):
            mimetype = 'application/octet-stream'
        elif fname.endswith('.txt'):
            mimetype = 'text/plain'
        else:
            raise ValueError(f'{fname} file extension is not recognized.')

if __name__ == '__main__':
    drive = Drive()


