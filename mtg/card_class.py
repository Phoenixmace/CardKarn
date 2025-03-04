from logging.config import valid_ident

import scrython
import json

from attr import attributes

from mtg.data_management import get_data, dump_data
import requests
# what if wrong set/name code
# setattr make sure all attributes are named the same wether loaded or not
# make other lists than main first man
#[[scryfall_dict_path],side_related, save_to_memory, save_to_collection, save_to_version, only_frontside matters(if siderelated)]
# redo price finding with version
scryfall_attribute_dict = {
    'name': [['name'], True, True, False,False, False],
    'layout': [['layout'], False, True, False, False],
    'image_uris': [['image_uris'], False, True, False, True, False], # false bc is dict
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
    'game_changer': [['game_changer'], False, True, False, False],
                  }
local_dict = {
    'language': [False, True, True, True],
    'finish': [False, True, True, True],
    'number': [False, True, True, True],
    'card_types': [False, True, False, False],
    'subtypes': [False, True, False, False],
    'supertypes': [False, True, False, False],
    'version_key': [False, True, True, True],
'salt': [False, True, False, False],
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
            self.save_to_memory()

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
        for attribute in scryfall_attribute_dict:
            if scryfall_attribute_dict[attribute][1]:
                if len(scryfall_attribute_dict[attribute]) == 6 and scryfall_attribute_dict[attribute][5]:
                    value = getattr(self, f'{attribute}_side_1')
                    setattr(self, attribute, value)
                else:
                    value_front = getattr(self, f'{attribute}_side_1')
                    value_back = getattr(self, f'{attribute}_side_2')
                    setattr(self, attribute, str(value_front)+'//'+str(value_back))

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

    def save_to_memory(self, del_after=False): # are side related stuff impemeted
        card_dict = self.to_dict()
        memory_data = get_data()

        if self.key in memory_data['memory']:
            # add attributes from scryfall
            for attribute in scryfall_attribute_dict:
                attribute_list = scryfall_attribute_dict[attribute]
                if attribute_list[2] and (not attribute_list[4]):
                    memory_data['memory'][self.key][attribute] = card_dict[attribute]
                elif attribute_list[4]:
                    memory_data['memory'][self.key]['versions'][self.version_key][attribute] = card_dict['versions'][self.version_key][attribute]

            # add others
            for attribute in local_dict:
                attribute_list = local_dict[attribute]
                if (attribute_list[1] or attribute_list[2]) and (not attribute_list[3]):
                    # version dependant
                    if attribute_list[0]:
                        memory_data['memory'][self.key][f'{attribute}_side_1'] = card_dict[f'{attribute}_side_1']
                        memory_data['memory'][self.key][f'{attribute}_side_2'] = card_dict[f'{attribute}_side_2']

                    memory_data['memory'][self.key][attribute] = card_dict[attribute]
                elif attribute_list[3]:
                    # version dependant
                    if attribute_list[0]:
                        memory_data['memory'][self.key]['versions'][self.version_key][f'{attribute}_side_1'] = card_dict['versions'][self.version_key][f'{attribute}_side_1']
                        memory_data['memory'][self.key]['versions'][self.version_key][f'{attribute}_side_2'] = card_dict['versions'][self.version_key][f'{attribute}_side_2']
                    memory_data['memory'][self.key]['versions'][self.version_key][attribute] = card_dict['versions'][self.version_key][attribute]


        else:
            memory_data['memory'][self.key] = card_dict
        dump_data(memory_data)
        if del_after:
            del self

    def to_dict(self):
        card_dict = {'versions':{self.version_key:{}}}

        # combine all attributes
        attribute_dict = {}
        for attribute in scryfall_attribute_dict:
            attribute_dict[attribute] = scryfall_attribute_dict[attribute]
        for attribute in local_dict:
            attribute_dict[attribute] = [[]]
            for item in local_dict[attribute]:
                attribute_dict[attribute].append(item)



        # version specific attributes key->versions-> setcode_f/n
        for attribute in attribute_dict:
            attribute_list = attribute_dict[attribute]
            if attribute_list[2] or attribute_list[3]:

                # get values
                value = getattr(self, attribute)
                card_dict[attribute] = value
                # sides
                if self.two_sided and attribute_list[1]:
                    value_1 = getattr(self, f'{attribute}_side_1')
                    value_2 = getattr(self, f'{attribute}_side_2')

                # insert values
                if not attribute_list[4]:
                    card_dict[attribute] = value
                    if self.two_sided:
                        card_dict[f'{attribute}_side_2'] = value_1
                        card_dict[f'{attribute}_side_1'] = value_2
                else:
                    card_dict['versions'][self.version_key][attribute] = value
                    if self.two_sided:
                        card_dict['versions'][self.version_key][f'{attribute}_side_2'] = value_1
                        card_dict['versions'][self.version_key][f'{attribute}_side_1'] = value_2

        return card_dict

    def save_to_collection(self, subfolder='main', delete_after=False):

        data = get_data() # get data
        card_dict = self.to_dict()

        # combine all attributes
        attribute_dict = {}
        for attribute in scryfall_attribute_dict:
            attribute_dict[attribute] = scryfall_attribute_dict[attribute]
        for attribute in local_dict:
            attribute_dict[attribute] = [[]]
            for item in local_dict[attribute]:
                attribute_dict[attribute].append(item)

        # check if relevant data was provided
        for attribute in attribute_dict:
            if attribute_dict[attribute][3] and not hasattr(self, attribute):
                print(f'{attribute} is missing to successfully save {self.name}')
                return False

        # create subfolder
        if subfolder not in data['collection']:
            data['collection'][subfolder] = {}

        if self.key in data['collection'][subfolder]:
            # already exists
            if self.version_key in data['collection'][subfolder][self.key]['versions']:
                data['collection'][subfolder][self.key]['versions'][self.version_key]['number'] += self.number
            else:
                # create version dict
                data['collection'][subfolder][self.key]['versions'][self.version_key] = {}
                for key in card_dict['versions'][self.version_key]:
                    if attribute_dict[key][3]:
                        data['collection'][subfolder][self.key]['versions'][self.version_key][key] = card_dict['versions'][self.version_key][key]

        # if not already saved
        else:
            # create card dict
            data['collection'][subfolder][self.key] = {}
            data['collection'][subfolder][self.key]['versions'] = {}
            data['collection'][subfolder][self.key]['versions'][self.version_key] = {}

            for key in attribute_dict:
                # not version related
                if not attribute_dict[key][4] and attribute_dict[key][3]:
                    data['collection'][subfolder][self.key][key] = card_dict[key]
                # version related
                elif attribute_dict[key][4]:
                    data['collection'][subfolder][self.key]['versions'][self.version_key][key] = card_dict['versions'][self.version_key][key]
        dump_data(data)
        if delete_after:
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


