import os
import pickle

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

API_key = 'insert_your_api_key'


class ApiManager:
    """
    Builds Google Drive/Docs API specified objects
    """

    creds = None
    _drive_service = None
    _docs_service = None
    scopes = []

    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/documents']
        self.creds = login(self.scopes)
        self.drive_service = build_drive(self.creds)
        self._docs_service = build_docs(self.creds)

    @property
    def drive_service(self):
        return self._drive_service

    @drive_service.setter
    def drive_service(self, value):
        self._drive_service = value

    @property
    def docs_service(self):
        return self._docs_service

    @docs_service.setter
    def docs_service(self, value):
        self._docs_service = value


class ItemList:
    """
    Stores a list of "File Resources".

    Users are encouraged to access modify ItemList through ItemListManager.
    """

    _item_list = []

    def __init__(self, item_list=None):
        if item_list:
            self.item_list.extend(item_list)

    @property
    def item_list(self):
        return self._item_list

    @item_list.setter
    def item_list(self, value):
        self._item_list = value


class ItemListManager:
    """
    Retrieve/manipulate "File Resource" objects
    """

    api_manager: ApiManager
    itemList: ItemList

    def __init__(self, itemList: ItemList):
        self.api_manager = ApiManager()
        self.itemList = itemList

    def name_to_id(self, name: str):
        for i in self.itemList.item_list:
            if i['name'] == name:
                return i['id']
        return None

    def retrieve_list(self, file_id='root'):
        results = self.api_manager.drive_service.files().list(pageSize=100,
                                                              q="'" + file_id + "' in parents",
                                                              fields="nextPageToken, files(id, name, mimeType)").execute()
        # list of dictionaries
        items = results.get('files', [])
        self.itemList.item_list = items

    def _sort_files_folders(self):
        temp_files = self.itemList.item_list[:]
        temp_folders = []
        for i in self.itemList.item_list:
            if isinstance(i, dict):
                if i['mimeType'] == 'application/vnd.google-apps.folder':
                    index = temp_files.index(i)
                    temp_files.pop(index)
                    temp_folders.append(i)
        self.itemList.item_list = temp_files + temp_folders

    def expand_folders(self, level=0):
        # no more levels left
        if level <= 0:
            return
        self._sort_files_folders()
        temp = []
        for i in self.itemList.item_list:
            temp.append(i)
            if i['mimeType'] == 'application/vnd.google-apps.folder':
                temp_item_list = ItemList()
                temp_item_list_mgr = ItemListManager(temp_item_list)
                temp_item_list_mgr.retrieve_list(i['id'])
                temp_item_list_mgr._sort_files_folders()
                temp_item_list_mgr.expand_folders(level - 1)
                temp.append([temp_item_list.item_list])
        self.itemList.item_list = temp

    def doc_extract(self) -> list:
        temp = []
        for i in self.itemList.item_list:
            if isinstance(i, list):
                temp_list = ItemList()
                temp_list.item_list = i
                item_list_manager = ItemListManager(temp_list)
                temp.extend(item_list_manager.doc_extract())
            if isinstance(i, dict):
                if i['mimeType'] == 'application/vnd.google-apps.document' or \
                        i['mimeType'] == 'application/vnd.google-apps.kix':
                    temp.append(i)
        return temp


def login(scopes):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # refresh or ...
            creds.refresh(Request())
        else:
            # login. get token (the object.)
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json',
                                                             scopes)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            # save
            pickle.dump(creds, token)
    return creds


def build_drive(creds):
    return build('drive', 'v3', credentials=creds, developerKey=API_key)


def build_docs(creds):
    return build('docs', 'v1', credentials=creds)


def file_probe(folder, level=0):
    temp = []
    if not isinstance(folder, list):
        return ['---' * level + str(folder)]
    for i in folder:
        temp.extend(file_probe(i, level + 1))
    return temp


def file_probe_v2(itemList, level=0):
    temp = []
    if isinstance(itemList, ItemList):
        folder = itemList.item_list
    else:
        folder = itemList
    if not isinstance(folder, list):
        return ['---' * level + str(folder['name'])]
    for i in folder:
        temp.extend(file_probe_v2(i, level + 1))
    return temp
