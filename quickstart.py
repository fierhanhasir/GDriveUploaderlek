from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from apiclient import errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_id.json'
APPLICATION_NAME = 'Drive API Python Quickstart'


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def insert_subfolder(service, title, parent_id):
	body = { 'name': title, 'mimeType': 'application/vnd.google-apps.folder'}

	if parent_id:
		body['parents'] = [parent_id]

	try:
		file = service.files().create(body=body).execute()
		return file

	except errors.HttpError as error:
		return ('An error occurred: %s' % error)


def get_service():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    return service


def show_all_files(service):
	results = service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
	items = results.get('files', [])
	if not items:
		print('No files found.')
	else:
		print('Files:')
		for item in items:
			print('{0} ({1})'.format(item['name'], item['id']))

def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    service = get_service()

    show_all_files(service)

if __name__ == '__main__':
    main()