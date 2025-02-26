from logging.config import valid_ident

import scrython
import json
from mtg.data_management import get_data, dump_data
import requests
# what if wrong set/name code
# setattr make sure all attributes are named the same wether loaded or not
# make other lists than main first man
#[[scryfall_dict_path],side_related, save_to_memory, save_to_collection, save_to_version, only_frontside matters(if siderelated)]
# redo price finding with version
scryfall_attribute_dict = {
    'name': [['name'], False, True, False,False],
    'layout': [['layout'], False, True, False, False],
    'image_uris': [['image_uris'], True, True, False, True, False], # false bc is dict
    'mana_cost': [['mana_cost'], True, True, False, False, True],
    'cmc': [['cmc'], False, True, False, False],
    'typeline': [['type_line'], True, True, False, False, False],
    'power': [['power'], True, True, False, False, True], # check if creature and maybe both sides if backside is creature
    'toughness': [['toughness'], True, True, False, True],
    'color_identity': [['color_identity'], False, True, False, False],
    'keywords': [['keywords'], False, True, False, False],
    'ruling': [['oracle_text'], True, True, False, False, False],
    'legality': [['legalities'], False, True, False, False],
    'game_changer': [['game_changer'], False, True, False, False],
    'set_code': [['set'], False, True, True, True],
    'rarity': [['rarity'], False, True, True, True],
    'edhrec_rank': [['edhrec_rank'], False, True, False, False],
    'cm_price': [['prices', 'eur'], False, True, True, True],
                  }
local_dict = {
    'language': [False, True, True, False],
    'finish': [False, True, True, True],
    'number': [False, True, True, True],
    'card_types': [False, True, False, False],
    'subtypes': [False, True, False, False],
    'supertypes': [False, True, False, False],
}
other_dict = {
    'salt': [False, True, False, False],
}

class Card():
    def __init__(self, name, number=1, set_code=None, finish='nonfoil', language='eng', just_use_cheapest=False, update_card=False):
        self.name = name
        self.set_code = set_code
        # search memory
        self.key = str(name).lower().replace(' ', '_')
        bulkdata = get_data()
        if set_code and self.key in bulkdata['memory'] and not update_card:
            # make version key
            self.version_key = f'{set_code}_{finish[0]}'

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
            # save memory

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
        for attribute in scryfall_attribute_dict:
            attribute_list = scryfall_attribute_dict[attribute]
            if not self.two_sided or not attribute_list[1]: # if general attribute or no double side
                value = self.scryfall_dict
                for path_step in attribute_list[0]:
                    if path_step in value:
                        value = value[path_step]
                    else:
                        value = None
                setattr(self, attribute, value)
            else: # if it is side dependant and there are 2 sides
                for side_index, side_dict in enumerate(self.scryfall_dict['card_faces']):
                    value = side_dict
                    for path_step in attribute_list[0]:
                        if path_step in value:
                            value = value[path_step]
                        else:
                            value = None
                    setattr(self, f'{attribute}_side_{side_index+1}', None)
        # set salt score
        self.set_salt_score()

        # combine sides and list card types
        if self.two_sided:
            self.combine_sides()
        self.set_types()
        return True
    def combine_sides(self):
        for attribute in scryfall_attribute_dict:
            if scryfall_attribute_dict[attribute][1]:
                if scryfall_attribute_dict[attribute][5]:
                    value = getattr(self, f'{attribute}_side_1')
                    setattr(self, attribute, value)
                else:
                    value_front = getattr(self, f'{attribute}_side_1')
                    value_back = getattr(self, f'{attribute}_side_2')
                    setattr(self, attribute, value_front+'//'+value_back)

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
        if self.two_sided:
            url_end = self.name_side_1 #idea for var name Luc
        else:
            url_end = self.name


        cleaned_name = name.lower()
        replace_char_dict = {
            'ó':'o',
            ' ':'-',
            '!':'',
            ',':'',
            '\'':'',
        }
        for char in replace_char_dict:
            cleaned_name = cleaned_name.replace(char, replace_char_dict[char])
        cleaned_name = cleaned_name.replace(' ', '-')
        cleaned_name = cleaned_name.replace('ó', 'o')
        url = f'https://json.edhrec.com/pages/cards/{cleaned_name}.json'
        print(url)
        try:
            edhrec_data = requests.get(url).json()
        except:
            print('Error getting Data', self.name)
            return
        salt = edhrec_data['container']['json_dict']['card']['salt']
        print(salt)
        self.salt = salt
        print(self.salt)
        if not self.cm_price:
            self.cm_price = edhrec_data['container']['json_dict']['card']['prices']['cardmarket']['price']

    def get_subtypes(self, typeline):
        subtypes = []
        if '—' in typeline:
            substr = typeline[typeline.index('—')+2:].split(' ')
            for creature_type in substr:
                subtypes.append(creature_type)
            return subtypes
        else:
            return subtypes
    def get_supertypes(self, typeline):
        supertypes = []
        possible_supertypes = ['Legendary', 'Tribal', 'Basic', 'Snow']
        for supertype in possible_supertypes:
            if supertype in typeline:
                supertypes.append(supertype)
        return supertypes
    def get_maintypes(self, typeline):
        main_types = []
        possible_main_types = ['Creature', 'Planeswalker', 'Battle', 'Land', 'Artifact', 'Instant', 'Sorcery', 'Enchantment']
        for main_type in possible_main_types:
            if main_type in typeline:
                main_types.append(main_type)
        return main_types

    def save_to(self, main_folder='bulk', subfolder='main', del_after_save=False):
        # Read the existing data from the JSON file
        data = get_data() # get data
        # set setkey
        if self.foil:
            version_key = self.set_code + '_f'
            version_key = (version_key.lower()).replace(' ', '_')
        elif self.set_code:
            version_key = self.set_code + '_n'
            version_key = (version_key.lower()).replace(' ', '_')
        else:
            print(f'cannot save {self.name}')


        # create necessairy paths
        if main_folder not in data:
            data[main_folder] = dict()
        if subfolder not in data[main_folder] and subfolder:
            data[main_folder][subfolder] = dict()

        # if subfolder provided
        if subfolder:
            # case card not yet added
            if self.key not in data[main_folder][subfolder]:
                data[main_folder][subfolder][self.key] = self.to_dict()
            #in case of the same set code add number of card
            elif version_key in data[main_folder][subfolder][self.key]['versions']:
                data[main_folder][subfolder][self.key]['versions'][version_key]['number'] += self.number
            # card saved but not the version
            else:
                data[main_folder][subfolder][self.key]['versions'][version_key] = self.to_dict()['versions'][version_key]
            dump_data(data)

        else: #no subfolder
            # case card not yet added
            if self.key not in data[main_folder]:
                data[main_folder][self.key] = self.to_dict()
            # in case of the same set code add number of card
            elif version_key in data[main_folder][self.key]['versions']:
                data[main_folder][self.key]['versions'][version_key]['number'] += self.number
            # card saved but not the version
            else:
                data[main_folder][self.key]['versions'][version_key] = self.to_dict()['versions'][version_key]
            dump_data(data)
        if del_after_save:
            del self

    def to_dict(self):
        # version specific attributes key->versions-> setcode_f/n
        save_to_versions = ['set_code', 'foil', 'number', 'cm_price', 'image_uris']
        if self.foil:
            version_key = self.set_code + '_f'
            version_key = (version_key.lower()).replace(' ', '_')
        else:
            version_key = self.set_code + '_n'
            version_key = (version_key.lower()).replace(' ', '_')
        dict_ = {}
        dict_['versions'] = {}
        dict_['versions'][version_key] = {}
        for attr in dir(self):
            # Get the attribute value
            value = getattr(self, attr)
            # Check if the attribute value is an instance of str and not a method or built-in attribute
            if (isinstance(value, str) or isinstance(value, float) or isinstance(value, int) or isinstance(value, list) or isinstance(value, dict)) and not callable(value) and not attr.startswith('__'):
                if attr in save_to_versions:
                    dict_['versions'][version_key][attr] = value
                else:
                    dict_[attr] = value
        return dict_

    def load_g(self, folder, subfolder=None):
        data = get_data()
        # get versionkey
        version_key = self.version_key

        # in case subfolder is given
        if subfolder:
            if version_key in data[folder][subfolder][self.key]['versions']:
                for attr in data[folder][subfolder][self.key]:
                    setattr(self, attr, data[folder][subfolder][self.key][attr])
                for attr in data[folder][subfolder][self.key]['versions'][version_key]:
                    setattr(self, attr, data[folder][subfolder][self.key]['versions'][version_key][attr])
        else:
            if version_key in data[folder][self.key]['versions']:
                for attr in data[folder][self.key]:
                    setattr(self, attr, data[folder][self.key][attr])
                for attr in data[folder][self.key]['versions'][version_key]:
                    setattr(self, attr, data[folder][self.key]['versions'][version_key][attr])
        del data
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


