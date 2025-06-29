from models.Deckbuilder import Deckbuilder

db = Deckbuilder('Niv-Mizzet, Parun', budget=100, model_name='adjusted_binary_small_testing_model')
db.build_deck()

