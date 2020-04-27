import os
import pickle

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request



# flow(oauth), request - auth, discovery - to build
# token 'creds' - access and refresh tokens. created automatically

def main():
    creds = login()
    drive_service = build_drive(creds)

    a = sort_files_folders(retrieve_list(drive_service))
    b = expand_folders(drive_service, a, 1)
    c = file_probe_v2(b)
    # # discovery and oauth(flow)
    # service = build('docs', 'v1', credentials=creds)
    # # actual document
    # document = service.documents().get(documentId=DOCUMENT_ID).execute()
    # print('The title is {}'.format(document.get('title')))
    # print(file_probe(['g', 'h', 'i', ['a', ['b', 'c', ['d', 'e']], 'f']], 0))

    for i in c:
        print(i)


def login():
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
              'https://www.googleapis.com/auth/documents.readonly']
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
                                                             SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            # save
            pickle.dump(creds, token)
    return creds


def build_drive(creds):
    return build('drive', 'v3', credentials=creds)


def retrieve_list(service, file_id='root'):
    results = service.files().list(pageSize=100,
                                   q="'" + file_id + "' in parents",
                                   fields="nextPageToken, files(id, name, mimeType)").execute()
    items = results.get('files', [])
    return items
    # if not items:
    #     print('No files found.')
    # else:
    #     print('Files:')
    #     print(items)
    #     for item in items:
    #         print(u'{0} ({1})'.format(item['name'], item['mimeType']))


def file_probe(folder, level=0):
    # temp_str = ''
    # if not isinstance(folder, list):
    #     return str(folder)
    # for i in folder:
    #     temp_str = temp_str + ('---' * level+file_probe(i, level + 1)) + '\n'
    # return temp_str
    temp = []
    if not isinstance(folder, list):
        return ['---' * level + str(folder)]
    for i in folder:
        temp.extend(file_probe(i, level + 1))
    return temp


def file_probe_v2(folder, level=0):
    # temp_str = ''
    # if not isinstance(folder, list):
    #     return str(folder)
    # for i in folder:
    #     temp_str = temp_str + ('---' * level+file_probe(i, level + 1)) + '\n'
    # return temp_str
    temp = []
    if not isinstance(folder, list):
        return ['---' * level + str("folder['name']")]
    for i in folder:
        temp.extend(file_probe(i, level + 1))
    return temp


def sort_files_folders(items):
    temp_files = items[:]
    temp_folders = []
    for i in items:
        if i['mimeType'] == 'application/vnd.google-apps.folder':
            index = temp_files.index(i)
            temp_files.pop(index)
            temp_folders.append(i)
    return temp_files + temp_folders


def expand_folders(service, sorted_items, level):
    if len(sorted_items) == 0:
        return sorted_items
    # no more levels left
    if level <= 0:
        return sorted_items
    temp = []
    for i in sorted_items:
        temp.append(i)
        if i['mimeType'] == 'application/vnd.google-apps.folder':
            retrieved_list = retrieve_list(service, i['id'])
            # returns a list of file resource objects
            n_sorted_items = sort_files_folders(retrieved_list)
            temp.append(
                [expand_folders(service, n_sorted_items, level - 1)])
    return temp


if __name__ == '__main__':
    main()
