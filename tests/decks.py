from models.Deckbuilder import Deckbuilder

decks = [
    ['Giada, Font of Hope', 0],
    ['Sythis, Harvest\'s Hand', 0],
    ['Arabella, Abandoned Doll', 0],
    ['Prosper, Tome-Bound', 500],
    ['Urza, Lord High Artificer', 10000],
    ['Nekusar, the Mindrazer', 0],
    ['Storm, Force of Nature', 100],
    ['Omnath, Locust of Creation', 500],
]
decks = [['Niv-Mizzet, Parun', 0],
         ['Giada, Font of Hope', 0],
         ['Norin the Wary', 0],
         ]


for deck in decks:
    db = Deckbuilder(deck[0], budget=deck[1], model_name='adjusted_binary_small_testing_model', card_weight=0.5)
    db.build_deck()
    exit()