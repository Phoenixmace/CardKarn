from util.machine_learning.tokenize import create_card_tokenizer, tokenize_cards
from models.Card import BaseCard

card = BaseCard({'name': 'Hengegate Pathway'})
card2 = BaseCard({'name': 'Demonic Tutor'})

create_card_tokenizer.create_oracle_tokenizer(name='oracle_test_tokenizer')
create_card_tokenizer.create_card_tokenizer(name='card_test_tokenizer')
for card in [card, card2]:
    print(tokenize_cards.tokenize_card(card, oracle_tokenizer_name='oracle_test_tokenizer', card_model_name='card_test_tokenizer'))