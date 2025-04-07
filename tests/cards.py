from models.Card import Card
from models.Deck import Deck
import util

# cards
test_cards = ['Treasure_token', "Demonic Tutr", 'elspeth', 'fjdklaöfjkö', 'Beyeen Veil // Beyeen Coast']
set_cards = [['Demonic Tutor', 'cmm'], ['Demonic Tutor', 'jfkdlöa']]

cards = []
for card in test_cards:
    testcard = Card(card)
    cards.append(testcard)
for card in set_cards:
    testcard = Card(name=card[0], set_code=card[1])
    cards.append(testcard)

for card in cards:
    if card.is_valid:
        card.add_to_collection()