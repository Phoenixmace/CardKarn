from models.Deckbuilder import Deckbuilder


db = Deckbuilder('Sliver Legion', budget=100, model_name='adjusted_binary_small_testing_model', card_weight=0.3)
db.build_deck()
db = Deckbuilder('The Ur-Dragon', budget=100, model_name='adjusted_binary_small_testing_model', card_weight=0.3)
db.build_deck()

