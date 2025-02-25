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
    cards = ['fdjaklfjdkalöfjkdslöa', 'Cruel Somnophage // Can"t Wake Up', 'Treasure Token', 'Jin-Gitaxias // The great Synthesis', 'alive // Well', 'budoka gardener // dokai weaver of life', 'aberrant researcher // perfected-form', 'argoth sanctum of nature', 'Beastbreaker of Bala Ged', 'Alchemist\'s Talent', 'Auspicious Starrix', 'Arcane Proxy', 'invasion of Ikoria', 'Agyrem', 'A Display of My Dark Power', 'Akroma, Angel of Wrath Avatar', 'Angel - Angel', 'Ajani, Adversary of Tyrants Emblem', 'bat-', 'adorable kitten', 'Abhorrent Oculus']
    cards_with_version = [['anointed-procession-anointed-procession', 'sld']]
    for card in cards:
        try:
            card_object = Card('Angel - Angel')
            if not card_object._is_valid():
                del card_object
            else:
                card_object.print()
        except Exception as e:
            logger.error('Failed to upload to ftp: '+ str(e) + card)










