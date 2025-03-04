from logging.config import valid_ident

import scrython
import json

from attr import attributes

from mtg.data_management import get_data, dump_data
import requests
# what if wrong set/name code
# make other lists than main first man

# [Source, Path, Side-related, Save to memory, Save to collection, Version-dependent, Only frontside matters, Data type]
attribute_dict = {
    'name': ['scryfall', ['name'], True, True, False, False, False, 'str'],
    'layout': ['scryfall', ['layout'], False, True, False, False, None, 'str'],
    'image_uris': ['scryfall', ['image_uris'], False, True, False, True, False, 'dict'],
    'mana_cost': ['scryfall', ['mana_cost'], True, True, False, False, True, 'str'],
    'cmc': ['scryfall', ['cmc'], False, True, False, False, None, 'int'],
    'typeline': ['scryfall', ['type_line'], True, True, False, False, False, 'str'],
    'power': ['scryfall', ['power'], True, True, False, False, True, 'int'],
    'toughness': ['scryfall', ['toughness'], True, True, False, True, False, 'int'],
    'color_identity': ['scryfall', ['color_identity'], False, True, False, False, None, 'list'],
    'keywords': ['scryfall', ['keywords'], False, True, False, False, None, 'list'],
    'ruling': ['scryfall', ['oracle_text'], True, True, False, False, False, 'str'],
    'legality': ['scryfall', ['legalities'], False, True, False, False, None, 'dict'],
    'game_changer': ['scryfall', ['game_changer'], False, True, False, False, None, 'str'],
    'set_code': ['scryfall', ['set'], False, True, True, True, None, 'str'],
    'rarity': ['scryfall', ['rarity'], False, True, False, False, None, 'str'],
    'edhrec_rank': ['scryfall', ['edhrec_rank'], False, True, False, False, None, 'int'],
    'cm_price': ['scryfall', ['prices', 'eur'], False, True, True, True, None, 'float'],
    'language': ['local', None, False, True, True, False, None, 'str'],
    'finish': ['local', None, False, True, True, True, None, 'str'],
    'number': ['local', None, False, False, True, True, None, 'int'],
    'card_types': ['local', None, False, True, False, False, None, 'list'],
    'subtypes': ['local', None, False, True, False, False, None, 'list'],
    'supertypes': ['local', None, False, True, False, False, None, 'list'],
    'version_key': ['local', None, False, True, True, True, None, 'str'],
    'salt': ['edhrec', None, False, True, False, False, None, 'str']
}




class Card():
    def __init__(self, name, number=1, set_code=None, finish='nonfoil', language='eng', just_use_cheapest=False, update_card=False, no_setcode_required=True):
        self.name = name
        self.set_code = set_code
        self.finish = finish
        self.language = language
        self.number = number

        # search memory
        self.key = str(name).lower().replace(' ', '_')
        # make version key
        if set_code:
            self.version_key = f'{set_code}_{finish[0]}'

        bulkdata = get_data()

        if set_code and self.key in bulkdata['memory'] and not update_card and (self.version_key in bulkdata['memory'][self.key]['versions'] or no_setcode_required):
            # make version key
            if not self.set_code:
                self.set_code = next(iter(bulkdata['memory'][self.key]['versions']))[0:-2]
            for attribute in bulkdata['memory'][self.key]:
                if attribute != 'versions':
                    setattr(self, attribute, bulkdata['memory'][self.key][attribute])
            # version related attributes
            for attribute in bulkdata['memory'][self.key]:
                setattr(self, attribute, bulkdata['memory'][self.key][attribute])
            self.is_valid = True
        elif not self.set_card_from_scryfall(): # load card from
            print(f'{self.name} could not be initiated')
            self.is_valid = False
        else:
            self.is_valid = True
        if self.is_valid:
            self.save_to()

    def _is_valid(self):
        return self.is_valid

    def set_card_from_scryfall(self):
        search_params = {'fuzzy': self.name}
        if self.set_code:
            search_params['set'] = self.set_code
        # searches based on given params
        try:
            scryfall_data = scrython.cards.Named(**search_params)
            # print('made request')
        except:
            print(f'{self.name} not found')
            return False

        # if not exactly the same
        self.scryfall_dict = scryfall_data.__dict__['scryfallJson']
        self.two_sided = 'card_faces' in self.scryfall_dict
        # set attributes

        for attribute in attribute_dict:
            attribute_list = attribute_dict[attribute]
            if (not self.two_sided or not attribute_list[2]) and attribute_list[0] == 'scryfall': # if general attribute or no double side
                value = self.scryfall_dict
                for path_step in attribute_list[1]:
                    if path_step in value:
                        value = value[path_step]
                    else:
                        value = None
                setattr(self, attribute, value)
            elif attribute_list[0] == 'scryfall': # if it is side dependant and there are 2 sides
                for side_index, side_dict in enumerate(self.scryfall_dict['card_faces']):
                    value = side_dict
                    for path_step in attribute_list[1]:
                        if path_step in value:
                            value = value[path_step]
                        else:
                            value = None
                    setattr(self, f'{attribute}_side_{side_index+1}', value)
        # set version key
        if not self.set_code:
            self.set_code = scryfall_data['set_code']
        self.version_key = f'{self.set_code}_{self.finish[0]}'

        # set salt score
        self.set_salt_score()

        # combine sides and list card types
        if self.two_sided:
            self.combine_sides()
        self.set_types()
        return True

    def combine_sides(self):
        for attribute in attribute_dict:
            if attribute_dict[attribute][2]:
                if attribute_dict[attribute][6]: # only front
                    value = getattr(self, f'{attribute}_side_1')
                    setattr(self, attribute, value)
                else:
                    value_front = getattr(self, f'{attribute}_side_1')
                    value_back = getattr(self, f'{attribute}_side_2')
                    setattr(self, attribute, str(value_front)+' // '+str(value_back))

    def set_types(self):
        typeline_list = self.typeline.split('//')
        self.card_types = []
        self.subtypes = []
        self.supertypes = []
        list_of_mtg_supertypes = ["Basic", "Legendary", "Ongoing", "Snow", "World", "Tribal"]

        for typeline in typeline_list:
            split_typeline = typeline.split('-')
            # set subtypes
            if '-' in typeline and 'Creature' in typeline:
                subtype_list = split_typeline[1].split(' ')
                for subtype in subtype_list:
                    if subtype not in self.subtypes:
                        self.subtypes.append(subtype)

            # set subtypes and supertypes
            for type in split_typeline[0].split(' '):
                if type in list_of_mtg_supertypes:
                    self.supertypes.append(type)
                else:
                    self.card_types.append(type)

    def set_salt_score(self):

        # clean name for edhrec url
        if self.two_sided:
            url_end = self.name_side_1.lower() #idea for var name Luc
        else:
            url_end = self.name.lower()
        replace_char_dict = {
            'ó':'o',
            ' ':'-',
            '!':'',
            ',':'',
            '\'':'',
        }
        for char in replace_char_dict:
            url_end = url_end.replace(char, replace_char_dict[char])

        url = f'https://json.edhrec.com/pages/cards/{url_end}.json'
        print(url)
        try:
            edhrec_data = requests.get(url).json()
            if 'redirect' in edhrec_data and len(edhrec_data) < 3:
                url = f'https://json.edhrec.com/pages{edhrec_data['redirect']}.json'
                edhrec_data = requests.get(url).json()
        except:
            print('Error getting Data', self.name)
            salt = 0
        try:
            salt = edhrec_data['container']['json_dict']['card']['salt']
        except:
            print('no salt score found for ', self.name)
            salt = 0
        print(salt)
        self.salt = salt
        print(self.salt)

    def save_to(self, save_to_memory=True, del_after=False, update_values=False, subfolder='main'): # are side related stuff impemeted
        all_data = get_data()
        if save_to_memory:
            save_folder = all_data['memory']
        else:
            if subfolder not in all_data['collection']:
                all_data['collection'][subfolder] = {}
            save_folder = all_data['collection'][subfolder]

        if self.key not in save_folder or (update_values and not save_to_memory): # if not already saved and only for memory
            save_folder[self.key] = {'versions' :{self.version_key:{}}}
            for attribute in attribute_dict:
                attribute_list = attribute_dict[attribute]
                if (save_to_memory and attribute_list[3]) or (not save_to_memory and attribute_list[4]): # if should be saved

                    # get all values
                    values_list = []
                    values_list.append(getattr(self, attribute))
                    if attribute_list[2] and self.two_sided and save_to_memory: # set twosided stuff
                        values_list.append(getattr(self, f'{attribute}_side_{1}'))
                        values_list.append(getattr(self, f'{attribute}_side_{2}'))

                    # save all values
                    for index, value in enumerate(values_list):
                        # set keys
                        if index == 0:
                            key = attribute
                        else:
                            key = f'{attribute}_side_{index}'
                        if attribute_list[5]: # side related
                            save_folder[self.key]['versions'][self.version_key][key] = value
                        else:
                            save_folder[self.key][key] = value
        elif self.key in save_folder and not save_to_memory: # adjust values if card already present
            if self.version_key in save_folder[self.key]['versions']:
                save_folder[self.key]['versions'][self.version_key]['number'] += self.number
            else: # create version subdict
                save_folder[self.key]['versions'][self.version_key] = {}
                for attribute in attribute_dict:
                    attribute_list = attribute_dict[attribute]
                    if attribute_list[4] and attribute_list[5]: #if version and saved
                        value = getattr(self, attribute)
                        save_folder[self.key]['versions'][self.version_key][attribute]= value

                        # save them
        if save_to_memory:
            all_data['memory'] = save_folder
        else:
            all_data['collection'][subfolder] = save_folder
        dump_data(all_data)
        del all_data

        if del_after:
            del self

    def print(self):
        print('Name: ', self.name)
        if self.mana_cost:
            print('Cost: ', self.mana_cost)
        print('Typeline: ', self.typeline)
        print('Ruling:', self.ruling)
        print('Set: ', self.set_code)
        if hasattr(self, 'power') and hasattr(self, 'toughness'):
            print('P/T: ', self.power, '/', self.toughness)
        if hasattr(self, 'cm_price'):
            print('Price: ', self.cm_price)
        else:
            print('Price: No price found')
        print('-'*100)


