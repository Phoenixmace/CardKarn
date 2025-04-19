from models.Deck import Deck

deck = Deck('testing', 'commander', commander='Nekusar, the Mindrazer')
deck.print()
deck.generate_deck(100, load=True)
deck.print()