
def authenticate(login_save='credentials/gdrive-loginsave.pickle', 
                cred_fname='credentials/gdrive-credentials.json'):
    
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(login_save):
        with open(login_save, 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                                         cred_fname, SCOPES)
            #creds = flow.run_local_server(port=0)
            creds = flow.run_console()
        
        # Save the credentials for the next run
        with open(login_save, 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service


folder_codes = {
    'log_reports': '1gVPKTUne5pbNoTASsCLQYE5VKl3fR15y',
    'data_dumps': '1PRyLslqu-81MBbIPB_AB69Nw4GpnxU8r',
}

def upload(service, fname, gdrive_folder):
    file_metadata = {
                     'name': os.path.basename(fname), 
                     'parents': [folder_codes[gdrive_folder]],
                    }
    if fname.endswith('.csv'):
        mimetype = 'text/csv'
    elif fname.endswith('.pic'):
        mimetype = 'application/octet-stream'
    elif fname.endswith('.txt'):
        mimetype = 'text/plain'
    else:
        raise ValueError(f'{fname} file extension is not recognized.')

    media = MediaFileUpload(fname, mimetype=mimetype)
    
    # may throw BrokenPipeError! IDK HOW TO FIX
    file = service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    return file


def list_files(service):
    # Call the Drive v3 API
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    return [item for item in items]
