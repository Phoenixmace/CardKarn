from mtg.data_management import get_data
from mtg.imports import import_collection_from_manabox
from mtg.deck_class import Deck
from mtg.card_class import Card
import mtg.data_management
import scrython
import logging
logger = logging.getLogger('ftpuploader')

listd =[1, 3]
listd[0] = 2
print(listd)
# python C:\Users\maxce\PycharmProjects\mtg_test\main.py
if __name__ == '__main__':
    cards = ['Demonic Tutor','fdjaklfjdkalöfjkdslöa', 'Cruel Somnophage // Can"t Wake Up', 'Treasure Token', 'Jin-Gitaxias // The great Synthesis', 'alive // Well', 'budoka gardener // dokai weaver of life', 'aberrant researcher // perfected-form', 'argoth sanctum of nature', 'Beastbreaker of Bala Ged', 'Alchemist\'s Talent', 'Auspicious Starrix', 'Arcane Proxy', 'invasion of Ikoria', 'Agyrem', 'A Display of My Dark Power', 'Akroma, Angel of Wrath Avatar', 'Angel - Angel', 'Ajani, Adversary of Tyrants Emblem', 'bat-', 'adorable kitten', 'Abhorrent Oculus']
    cards_with_version = [['anointed-procession-anointed-procession', 'sld']]
    for card in cards:
        card_object = Card(card)
        if not card_object._is_valid():
            del card_object
        else:
            card_object.save_to_collection()
            card_object.save_to_memory()
            print(card_object.to_dict())











