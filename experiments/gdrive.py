


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
    default_cred_fname = 'credentials/gdrive-credential-cache.json'
    def __init__(self, secrets_fname, cred_fname=None, scopes=None, authenticate=True):

        self.scopes = scopes if scopes is not None else self.default_scopes
        
        self.secrets_path = pathlib.Path(secrets_fname)
        self.service = None

        # set up credentials cache file
        cred_fname = cred_fname if cred_fname is not None else self.default_cred_fname
        self.cred_path = pathlib.Path(cred_fname)
        self.creds = self.read_creds()

        if authenticate:
            self.authenticate()

    def read_creds(self):
        if self.cred_path.exists():
            return Credentials.from_authorized_user_file(self.cred_path, self.scopes)
        else:
            return None
    
    def write_creds(self):
        self.cred_path.parent.mkdir(parents=True, exist_ok=True)
        self.cred_path.write_text(self.creds.to_json())
        #with self.cred_path.open('w') as f:
        #    f.write(self.creds.to_json())
        
    def authenticate(self):
        '''Authenticate the application and save service and credentials.
        '''
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                                            self.secrets_path, self.scopes)
                #creds = flow.run_local_server(port=0)
                self.creds = flow.run_console()
            
            # Save the credentials for the next run
            self.write_creds()

        self.service = build('drive', 'v3', credentials=self.creds)

        return self

    def print_files(self, target):
        results = self.service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))


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
        file = self.service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()
        return file
            
    def mimetype_lookup(self, fname):
        return 'application/octet-stream'
        if fname.endswith('.csv'):
            mimetype = 'text/csv'
        elif fname.endswith('.pic'):
            mimetype = 'application/octet-stream'
        elif fname.endswith('.txt'):
            mimetype = 'text/plain'
        else:
            raise ValueError(f'{fname} file extension is not recognized.')

if __name__ == '__main__':
    drive = Drive('credentials/client_secret_4175.json')
    drive.print_files('1NHEvd4auC4jmFZbh-KUPsicYs6zVcGRf')
    drive.upload_file('tmp.txt', '1NHEvd4auC4jmFZbh-KUPsicYs6zVcGRf')

