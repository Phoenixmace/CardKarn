import requests
from util.machine_learning import card_array
from util.database import sql_card_operations

# [Source, Path, Side-related, Save to memory, Save to collection, Version-dependent, Only frontside matters, Data type]
non_scryfall_attributes = ['salt']
additional_attributes = ['number', 'language', 'finish']




class BaseCard():
    def __init__(self,search_params=None, update=False, save_changes=True):

        recieved_dict = sql_card_operations.get_card_dict(search_params)
        if not recieved_dict:
            print('failed to initiate card', search_params)
            del self
            return
        self.__dict__ = recieved_dict

        # set new data
        for i in [i for i in non_scryfall_attributes if (not hasattr(self, i) or update)]:
            function_name = f'set_{i}'
            method = getattr(self, function_name, None)
            if callable(method):
                method()
        if save_changes:
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

    def store_base_card_dict(self):
        sql_card_operations.update_card(self.__dict__)



class Card(BaseCard):
    def __init__(self, args):
        for attribute in args:
            if attribute in additional_attributes:
                setattr(self, attribute, args[attribute])