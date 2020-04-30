from Document import DocItemListConnector
from DriveComponent import ItemListManager, ItemList


def main():
    a = UserSetup()
    a.start()


class UserSetup:
    current_item_list = None
    item_list_manager = None

    def __init__(self):
        self.current_item_list = ItemList()
        self.item_list_manager = ItemListManager(self.current_item_list)

    def start(self):
        self.item_list_manager.retrieve_list()
        self.item_list_manager.expand_folders(1)
        # a = file_probe_v2(self.current_item_list)
        # for i in a:
        #     print(i)
        b = self.item_list_manager.doc_extract()

        connector = DocItemListConnector(b)
        document_list = connector.document_list
        print("done")

if __name__ == '__main__':
    main()
