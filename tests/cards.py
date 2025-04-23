from models.Deck import Deck
from util import card_util
arg = [{'name': 'Demonic Tutor', 'set':'cmm'}, {'name': "Cavern of Sould", 'set':'lci'}]

cards = card_util.get_cards(arg)
print(cards)