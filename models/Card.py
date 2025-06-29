import json
import time
from util.machine_learning.tokenize import tokenize_cards
import requests
from util.database import sql_card_operations
import threading
import numpy as np
# [Source, Path, Side-related, Save to memory, Save to collection, Version-dependent, Only frontside matters, Data type]
non_scryfall_attributes = ['salt']
additional_attributes = ['number', 'language', 'finish']




class BaseCard():
    def __init__(self,search_params=None, update=False, card_json=None, wait_for_salt_score=False, get_salt = False):
        self.is_valid = True
        if card_json:
            self.__dict__ = card_json

        else:
            recieved_dict = sql_card_operations.get_card_dict(search_params)
            if not recieved_dict:
                print('failed to initiate card', search_params)
                self.is_valid = False
                return
            self.__dict__ = recieved_dict

        # set new data
        if not hasattr(self, 'salt') and get_salt:
            self.set_salt(wait_for_salt_score)


    def set_salt(self, wait_for_salt_score):
        start_time = time.time()
        def fetch_salt():
            edhrec_url = self.related_uris['edhrec']
            try:
                response = requests.get(edhrec_url, timeout=2)
                if response.status_code == 200:
                    card_link = response.url.split('/')[-1]
                    json_url = f'https://json.edhrec.com/pages/cards/{card_link}.json'
                    json_response = requests.get(json_url, timeout=2)
                    if response.status_code == 200:
                        json_response_dict = json_response.json()
                        card_data = json_response_dict['container']['json_dict']['card']

                        # set attributes
                        self.salt = card_data['salt']
                        if isinstance(self.salt, str):
                            self.salt = float(self.salt)
                        self.store_base_card_dict()
            except requests.exceptions.RequestException as e:
                #print("Request failed:", e)
                pass
            if not hasattr(self, 'salt'):
                self.salt = None
        thread = threading.Thread(target=fetch_salt)
        thread.start()
        if wait_for_salt_score:
            thread.join()
        #print(f'Request took: {round(time.time() - start_time, 2)} seconds')

    def store_base_card_dict(self):
        sql_card_operations.update_card(self.__dict__)

    def get_np_array(self, method=1, weights={}, name=None,  oracle_tokenizer_name='oracle_tokenizer', card_tokenizer_name='card_tokenizer'):
        if not name:
            name = str(method)

        if not hasattr(self, 'tokenized'):
            self.tokenized = {}
        elif name in self.tokenized:
            two_arrays = json.loads(self.tokenized[name])
            oracle_tokens = np.array(two_arrays[0])
            card_tokens = np.array(two_arrays[1])
            return oracle_tokens, card_tokens

        oracle_tokenized, card_tokenized = tokenize_cards.tokenize_card(self, oracle_tokenizer_name=oracle_tokenizer_name, card_model_name=card_tokenizer_name)
        tokens_to_store = [oracle_tokenized.tolist(), card_tokenized.tolist()]
        self.tokenized[name] = json.dumps(tokens_to_store)
        self.store_base_card_dict()
        return oracle_tokenized, card_tokenized



