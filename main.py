from mtg.data_management import get_data
from mtg.imports import import_collection_from_manabox
from mtg.deck_class import Deck
from mtg.card_class import Card
import mtg.data_management




# python C:\Users\maxce\PycharmProjects\mtg_test\main.py
if __name__ == '__main__':
    #import_collection_from_manabox('C:\\Users\\maxce\\Downloads\\ManaBox_Collection.csv', True, True)
    deck = Deck('testdeck', commander='Yarok, the Desecrated')
    #edhrec = (deck._get_edhrec_data_())
    deck.generate_deck(10, load=True)
    print(deck.get_stats())
    #deck.print()


