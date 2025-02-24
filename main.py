from mtg.data_management import get_data
from mtg.imports import import_collection_from_manabox
from mtg.deck_class import Deck
from mtg.card_class import Card
import mtg.data_management
import scrython







# python C:\Users\maxce\PycharmProjects\mtg_test\main.py
if __name__ == '__main__':
    #card_night = Card('daybreak ranger')
    #card_double = Card('jin-gitaxias, the great synthesis')
    #card_adventure = Card('Cruel Somnophage // Can\'t Wake Up')
    #tutor = Card('diabolic intent')
    # print(card_adventure.salt, card_adventure.typeline)
    search_params = {'fuzzy': 'Cruel Somnophage'}

    scryfall_data = scrython.cards.Named(**search_params)
    print(getattr(scryfall_data, 'name'))
    print(scryfall_data.__getattribute__('name'))
    dicti = str(scryfall_data.__dict__).replace('\'', '"').replace('{', '{').replace('}', '}').replace(',',',\n')
    print(type(dicti) is dict, type(type(dict)))
    print(dicti)





