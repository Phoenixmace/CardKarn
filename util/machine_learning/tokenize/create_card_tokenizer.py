from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from util.database.sql_card_operations import get_all_cards_by_query
from util.data_util.data_util import get_data_path
import pickle

def create_oracle_tokenizer(name='oracle_tokenizer'):
    # get texts
    query = "SELECT oracle_text_front, oracle_text_back FROM cards"
    all_cards = get_all_cards_by_query(query)
    def combine_texts(card_texts):
        oracle_texts = []
        for side_text in card_texts:
            if side_text:
                oracle_texts.append(side_text)
        combined_text = " // ".join(oracle_texts)
        return combined_text
    tokenizer_path = get_data_path(f'{name}.pickle', ['neural_network', 'tokenizers'], allow_not_existing=True)
    texts = [combine_texts(card_texts) for card_texts in all_cards]
    tokenizer = Tokenizer(num_words=3000)
    tokenizer.fit_on_texts(texts)
    with open(tokenizer_path, 'wb') as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return tokenizer
def create_card_tokenizer(name='card_tokenizer'):
    # get texts
    query = "SELECT rarity, layout, mana_cost_front, mana_cost_back, type_line_front, type_line_back FROM cards"
    all_cards = get_all_cards_by_query(query)
    def combine_texts(card_texts):
        oracle_texts = []
        for side_text in card_texts:
            if side_text:
                oracle_texts.append(side_text)
        combined_text = " // ".join(oracle_texts)
        return combined_text
    tokenizer_path = get_data_path(f'{name}.pickle', ['neural_network', 'tokenizers'], allow_not_existing=True)
    texts = []
    for rarity, layout, mana_cost_front, mana_cost_back, type_line_front, type_line_back in all_cards:
        mana_cost = combine_texts([mana_cost_front, mana_cost_back])
        type_line = combine_texts([type_line_front, type_line_back])
        string = [rarity, layout, mana_cost, type_line]
        string = ", ".join(string)
        texts.append(string)

    tokenizer = Tokenizer(num_words=3000)
    tokenizer.fit_on_texts(texts)
    with open(tokenizer_path, 'wb') as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return tokenizer