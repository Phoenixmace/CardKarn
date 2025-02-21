from mtg.deck_class import Deck

decks_to_build = { #commander:budget
    'Arabella, Abandoned Doll': 0,
    'Nekusar, the Mindrazer': 0,
    'luc 0': 0,
    'Prosper, Tome-Bound': 100,
    'Storm, Force of Nature': 100,
    'luc 100': 100,
    'Muldrotha, the Gravetide': 500,
    'Omnath, Locus of Creation': 500,
    'luc 500': 500,
    'Urza, Lord High Artificer': 10000,
    'Sisay, Weatherlight Captain': 10000,
    'Ratadrabik of Urborg': 10000
}

for commander in decks_to_build:
    budget = decks_to_build[commander]
    deckname = f'{commander}_{int(budget)}_CardKarn'
    deck = Deck(deck_name=deckname, format='commander', commander=commander)
    deck.generate_deck(budget=budget)
    deck.save()