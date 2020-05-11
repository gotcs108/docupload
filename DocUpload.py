"""
Navigate drive and view documents using Google Drive/Docs API.
"""
from Document import DocItemListConnector
from DriveComponent import ItemListManager, ItemList, file_probe_v2


def main():
    """
    Initiates DocUpload
    """

    a = UserSetup()
    a.start()


class UserSetup:
    """
    Initiates the "setup" process.

    Instantiates objects for:
    1. Setup (retrieval, construction of necessary objects)
    2. Processing data
    3. Interaction with data.
    """

    current_item_list = None
    item_list_manager = None

    def __init__(self):
        self.current_item_list = ItemList()
        self.item_list_manager = ItemListManager(self.current_item_list)

    def start(self):
        self.item_list_manager.retrieve_list()
        # expand the folder level
        self.item_list_manager.expand_folders(0)
        # Below is an example code for the file tree
        # a = file_probe_v2(self.current_item_list)
        # for i in a:
        #     print(i)

        # Using item_list_manager, you can extract the files
        b = self.item_list_manager.doc_extract()

        # Below is an example code for converting extracted "file resources"
        # (google drive API) into a list of "Document" object
        # connector = DocItemListConnector(b)
        # document_list = connector.document_list
        # for i in document_list.documents:
        #     print(i.content)


if __name__ == '__main__':
    main()
