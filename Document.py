from typing import List

from DriveComponent import ApiManager


class Document:
    title = None
    content = None
    id = None
    mime = None

    def __init__(self, title: str, content: str, id: str, mime: str):
        self.title = title
        self.content = content
        self.id = str
        self.mime = str


class DocumentList:
    documents: List[Document] = []

    def __init__(self, documents: List[Document]):
        for i in documents:
            self.insert(i)

    def remove(self, document):
        self.documents.remove(document)

    def insert(self, document):
        if self.documents.count(document) == 0:
            self.documents.append(document)


class DocItemListConnector:
    list_of_items: List
    document_list: DocumentList

    def __init__(self, list_of_items: List):
        self.list_of_items = list_of_items
        doc_factory = DocFactory()
        list_of_documents = doc_factory.files_to_docs(self.list_of_items)
        self.document_list = DocumentList(list_of_documents)


class DocFactory:
    api_manager: ApiManager

    def __init__(self):
        self.api_manager = ApiManager()

    def file_to_doc(self, file: dict) -> Document:
        doc = self.api_manager.docs_service.documents().get(documentId=file['id']).execute()
        body = doc['body']
        name = file['name']
        file_id = file['id']
        mime = file['mimeType']
        document = Document(name, body, file_id, mime)
        return document

    def files_to_docs(self, file_list: List) -> List[Document]:
        docs_list = []
        for i in file_list:
            docs_list.append(self.file_to_doc(i))
        return docs_list
