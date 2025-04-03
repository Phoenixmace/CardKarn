from models.Card import Card
from models.Deck import Deck
import util

# cards
test_cards = ['Treasure_token', "Demonic Tutr", 'elspeth', 'fjdklaöfjkö']
set_cards = [['Demonic Tutor', 'cmm'], ['Demonic Tutor', 'jfkdlöa']]

cards = []
for card in test_cards:
    testcard = Card(card)
    cards.append(testcard)
for card in set_cards:
    testcard = Card(name=card[0], set_code=card[1])
    cards.append(testcard)

for card in cards:
    print(card.__dict__)
