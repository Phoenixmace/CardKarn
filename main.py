from mtg.deck_class import Deck
from mtg.card_class import Card




# python C:\Users\maxce\PycharmProjects\mtg_test\main.py
if __name__ == '__main__':
    deck = Deck('test', 'commander', commander='niv-mizzet_parun')
    print(deck._get_all_cards_for_building_(deck._get_edhrec_data_()))

