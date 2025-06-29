from models.Deckbuilder import Deckbuilder

db = Deckbuilder('Rivaz of the Claw', budget=100, model_name='adjusted_binary_small_testing_model', card_weight=0.3)
db.build_deck()
db = Deckbuilder('Sliver Legion', budget=100, model_name='adjusted_binary_small_testing_model', card_weight=0.3)
db.build_deck()

