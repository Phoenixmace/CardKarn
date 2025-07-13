from models.Deckbuilder import Deckbuilder
db = Deckbuilder('Giada, Font of Hope', budget=100, model_name='adjusted_binary_small_testing_model', card_weight=1)
db.build_deck()

