from mtg.data_management import get_data
from mtg.imports import import_collection_from_manabox
from mtg.deck_class import Deck
from mtg.card_class import Card
import mtg.data_management
import scrython
import logging
logger = logging.getLogger('ftpuploader')


# python C:\Users\maxce\PycharmProjects\mtg_test\main.py
if __name__ == '__main__':
    import_collection_from_manabox(file_path=r"C:\Users\maxce\Downloads\ManaBox_Collection_für_ma.csv", add_lists=True, all_main=True)










