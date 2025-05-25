import requests
from util.machine_learning import card_array
from util import card_util
from util.json_util import get_data, dump_data

# [Source, Path, Side-related, Save to memory, Save to collection, Version-dependent, Only frontside matters, Data type]
non_scryfall_attributes = ['salt']
additional_attributes = ['number', 'language', 'finish']




class BaseCard():
    def __init__(self, index=None,search_params=None, update=True):
        if not index and search_params:
            index = card_util.get_card_index(search_params)
        elif not not index:
            print('invalid card initiation')
            del self
        recieved_dict = card_util.get_card_dict(index)
        self.__dict__ = recieved_dict

        # set new data
        for i in [i for i in non_scryfall_attributes if (not hasattr(self, i) or update)]:
            function_name = f'set_{i}'
            method = getattr(self, function_name, None)
            if callable(method):
                method()
        self.store_base_card_dict()
        self.quick_store()

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

    def store_base_card_dict(self):
        data = get_data('card_values_to_update.json', subfolder='database')
        if str(self.index) not in data['cards']:
            data['cards'][str(self.index)] = self.__dict__
            dump_data('card_values_to_update.json', data=data,subfolder='database')

    def quick_store(self, update=False):
        short_card_data = get_data('short_cards.json', subfolder='database')
        relevant_keys = ['game_changer','mana_cost','oracle_id', 'cmc', 'color_identity', 'edhrec_rank', 'legalities', 'name', 'power', 'toughness', 'keywords', 'layout', 'prices', 'salt', 'type_line', 'oracle_text', 'rarity']
        short_dict = {key: self.__dict__[key] for key in relevant_keys if hasattr(self, key)}
        if  self.oracle_id not in short_card_data or update:
            short_card_data[self.oracle_id] = short_dict
            dump_data('short_cards.json', data=short_card_data,subfolder='database')
        return short_dict


class ShortCard():
    def __init__(self, oracle_id=None, index=None, search_params=None, update=False):
        data = get_data('short_cards.json', subfolder='database')

        if oracle_id and oracle_id in data and not update:
            self.__dict__ = data[oracle_id]
        elif index or search_params:
            self.__dict__ = BaseCard(index=index, search_params=search_params).quick_store(update=update)
        else:
            print('invalid card initiation')
            del self
    def save(self):
        dump_data('short_cards.json', data=self.__dict__,subfolder='database')

    def get_array(self, type='1'):
        # key model type: array, (edited) weights
        array_data = card_array.get_array(self, type=type)
        return array_data

class Card(BaseCard):
    def __init__(self, args):
        for attribute in args:
            if attribute in additional_attributes:
                setattr(self, attribute, args[attribute])