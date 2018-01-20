from __future__ import print_function
from typing import List
import httplib2
import os

from apiclient import discovery
from apiclient import errors
from googleapiclient.http import MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import re

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


class Manipulation:

	def __init__(self, parent):
		self.parent_id = parent
		self.credentials = self.get_credentials()
		self.service = self.get_service()

	def get_credentials(self):
		home_dir = os.path.expanduser('~')
		credential_dir = os.path.join(home_dir, '.credentials')
		if not os.path.exists(credential_dir):
			os.makedirs(credential_dir)
		credential_path = os.path.join(credential_dir, '.drive-python-quickstart.json')
		store = Storage(credential_path)
		credentials = store.get()
		if not credentials or credentials.invalid:
			flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
			flow.user_agent = APPLICATION_NAME
			if flags:
				credentials = tools.run_flow(flow, store, flags)
			else:
				credentials = tools.run(flow, store)
			print('Storing credentials to ' + credential_path)
		return credentials

	def get_service(self):
		http = self.credentials.authorize(httplib2.Http())
		service = discovery.build('drive', 'v3', http=http)
		return service

	def show_all(self):
		results = self.service.files().list(pageSize=10, fields='nextPageToken, files(id, name)')
		results.execute()
		items = results.get('files', [])
		if not items:
			print('No files found.')
		else:
			print('Files:')
			for item in items:
				print('{0} ({1})'.format(item['name'], item['id']))

	def create_subfolder(self, name, parent_id=None) -> str:
		body = {'name': name, 'mimeType': 'application/vnd.google-apps.folder'}
		if parent_id is None:
			parent_id = '1prL7ghxu56KOVaPMgyr-YGTuaeScvKye'
			body['parents'] = [parent_id]
		else:
			body['parents'] = [parent_id]

		try:
			file = self.service.files().create(body=body).execute()
			return file['id']

		except errors.HttpError as error:
			return ('An error occurred: %s' % error)

	def insert_image_file(self,name, parent_id, img_path) -> str:
		file_metadata = {
			'name': name
		}
		if parent_id:
			file_metadata['parents'] = [parent_id]
		media = MediaFileUpload(img_path, mimetype='image/jpeg', resumable=True)
		try:
			file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
			return file['id']

		except errors.HttpError as error:
			return ('An error occurred: %s' % error)

	def delete_items(self, item_id) -> bool:
		try:
			self.service.files().delete(fileId=item_id).execute()
			return True
		except:
			return False

	def get_item_id_list(self, parent_id=None) -> list:
		if parent_id is None:
			parent_id = self.parent_id

		result = []
		page_token = None
		while True:
			try:
				param = {}
				if page_token:
					param['pageToken'] = page_token
				children = self.service.files().list(q='\'' + parent_id + '\'' + '+in+parents', **param).execute()

				for child in children.get('items', []):
					result.append(child['id'])
				page_token = children.get('nextPageToken')
				if not page_token:
					break
			except errors.HttpError as error:
				result.append(error)
				break

		return result
