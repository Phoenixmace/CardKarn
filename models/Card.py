import time

import requests
from util.database import sql_card_operations
import threading
# [Source, Path, Side-related, Save to memory, Save to collection, Version-dependent, Only frontside matters, Data type]
non_scryfall_attributes = ['salt']
additional_attributes = ['number', 'language', 'finish']




class BaseCard():
    def __init__(self,search_params=None, update=False, card_json=None, wait_for_salt_score=False):
        if card_json:
            self.__dict__ = card_json
        else:
            recieved_dict = sql_card_operations.get_card_dict(search_params)
            if not recieved_dict:
                print('failed to initiate card', search_params)
                del self
                return
            self.__dict__ = recieved_dict

        # set new data
        if not hasattr(self, 'salt'):
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

    def get_np_array(self, method=1, weights={}, load_existing=False, name=None):
        pass