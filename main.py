from util.data_util.collection_import import import_collection_from_manabox
import logging
logger = logging.getLogger('ftpuploader')


# python C:\Users\maxce\PycharmProjects\mtg_test\main.py
if __name__ == '__main__':
    import_collection_from_manabox(file_path=r"C:\Users\maxce\Downloads\ManaBox_Collection_für_ma.csv", add_lists=True, all_main=True)










