from models.Deckbuilder import Deckbuilder

db = Deckbuilder('Niv-Mizzet, Parun', budget=100, model_name='binary_small_testing_model')
db.build_deck()

