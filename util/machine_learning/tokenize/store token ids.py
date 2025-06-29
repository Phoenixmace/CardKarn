from util.database.sql_card_operations import get_all_cards_by_query
from util.machine_learning.tokenize.tokenize_cards import tokenize_card
from models.Card import BaseCard
import json
from util.database.sql_util import get_cursor
from tqdm import tqdm
import numpy as np

def store_token_ids(oracle_tokenizer_name='oracle_tokenizer', card_tokenizer_name='card_tokenizer'):
    query = "SELECT scryfall_id, json FROM cards"
    all_cards = get_all_cards_by_query(query)
    def tokenize_and_save_card(card):
        card_json = json.loads(card[1])
        card_object = BaseCard(card_json=card_json, get_salt=False)
        scryfall_id = card[0]
        padded_oracle, padded_card = card_object.get_np_array(oracle_tokenizer_name=oracle_tokenizer_name, card_tokenizer_name=card_tokenizer_name)
        tokens = np.vstack([padded_oracle, padded_card])
        tokens = json.dumps(tokens.tolist())
        return [tokens, scryfall_id]

    conn, cursor = get_cursor('cards.db')
    chunk_size = 500
    all_params = []
    for card in tqdm(all_cards, desc='tokenizing cards'):
        card_list = tokenize_and_save_card(card)
        all_params.append(card_list)
        if len(all_params)%chunk_size==0:
            cursor.executemany("UPDATE cards set tokens = ? where scryfall_id = ? ", all_params)
            conn.commit()
            all_params = []
store_token_ids()

