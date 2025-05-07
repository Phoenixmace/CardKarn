from http.client import responses

import requests
import util
from util import card_util
from util.json_util import get_data, dump_data

# [Source, Path, Side-related, Save to memory, Save to collection, Version-dependent, Only frontside matters, Data type]
additional_attributes = ['number', 'set', 'language', 'finish']




class BaseCard():
    def __init__(self, index=None,search_params=None):
        if not index and search_params:
            index = card_util.get_card_index(search_params)
        elif not not index:
            print('invalid card initiation')
            del self
        recieved_dict = card_util.get_card_dict(index)
        self.__dict__ = recieved_dict

        # set new data
        self.set_salt()
        self.store_base_card_dict()

    def set_salt(self):
        edhrec_url = self.related_uris['edhrec']
        response = requests.get(edhrec_url)
        if response.status_code == 200:
            card_link = response.url.split('/')[-1]
            json_url = f'https://json.edhrec.com/pages/cards/{card_link}.json'
            json_response = requests.get(json_url)
            if response.status_code == 200:
                json_response_dict = json_response.json()
                card_data = json_response_dict['container']['json_dict']['card']

                # set attributes
                self.salt = card_data['salt']
                if isinstance(self.salt, str):
                    self.salt = float(self.salt)

        print()


    def store_base_card_dict(self):
        data = get_data('card_values_to_update.json', subfolder='database')
        if str(self.index) not in data['cards']:
            data['cards'][str(self.index)] = self.__dict__
            dump_data('card_values_to_update.json', data=data,subfolder='database')


class Card(BaseCard):
    def __init__(self, args):
        for attribute in args:
            if attribute in additional_attributes:
                setattr(self, attribute, args[attribute])