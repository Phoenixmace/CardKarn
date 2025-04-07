import scrython

from util.json_util import get_data, dump_data, set_value, increment_value_by
import requests
# what if wrong set/name code
# make other lists than main first man
# card faces to class

# [Source, Path, Side-related, Save to memory, Save to collection, Version-dependent, Only frontside matters, Data type]
attribute_dict = {
    'name': ['scryfall', ['name'], True, True, False, False, False, 'str'],
    'layout': ['scryfall', ['layout'], False, True, False, False, None, 'str'],
    'image_uris': ['scryfall', ['image_uris'], False, True, False, False, False, 'dict'],
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
    'version_key': ['local', None, False, False, False, True, None, 'str'],
    'salt': ['edhrec', None, False, True, False, False, None, 'str']
}




class Card():
    def __init__(self, name, number=1, set_code=None, finish='nonfoil', language='eng', just_use_cheapest=False, update_card=False, no_setcode_required=True, with_existing_scryfall=None):
        self.name = name
        self.set_code = set_code
        self.finish = finish
        self.language = language
        self.number = number
        # make keys
        self.key = str(name).lower().replace(' ', '_')
        if set_code:
            self.version_key = f'{set_code}_{finish[0]}'

        memory = get_data('memory.json')
        # if scryfall_data is provided
        if with_existing_scryfall and self.set_card_from_scryfall(existing_data=with_existing_scryfall):
            self.is_valid = True

        elif self.key in memory['cards'] and not update_card and (no_setcode_required or (hasattr(self, 'version_key') and self.version_key in memory['cards'][self.key]['versions'])):
            if not (hasattr(self, 'version_key') and self.version_key in memory['cards'][self.key]['versions']) and no_setcode_required:
                self.version_key = next(iter(memory['cards'][self.key]['versions']))
            for attribute in memory['cards'][self.key]:
                if attribute != 'versions':
                    setattr(self, attribute, memory['cards'][self.key][attribute])
            # version related attributes
            for attribute in memory['cards'][self.key]['versions'][self.version_key]:
                setattr(self, attribute, memory['cards'][self.key]['versions'][self.version_key][attribute])
            self.is_valid = True
        elif not self.set_card_from_scryfall(): # load card from
            print(f'{self.name} could not be initiated')
            self.is_valid = False
        else:
            self.is_valid = True
        if self.is_valid:
            self.save_to_memory()


    def set_card_from_scryfall(self, existing_data=None):
        if not existing_data:
            search_params = {'fuzzy': self.name}
            if self.set_code:
                search_params['set'] = self.set_code
            # searches based on given params
            try:
                scryfall_data = scrython.cards.Named(**search_params)
            except:
                print(f'{self.name} not found')
                return False

            self.scryfall_dict = scryfall_data.__dict__['scryfallJson']
        else:
            self.scryfall_dict = existing_data
        self.two_sided = 'card_faces' in self.scryfall_dict
        # set attributes
        # redefine potentially false stuff
        self.name = self.scryfall_dict['name']
        self.key = str(self.name).lower().replace(' ', '_')
        self.set_code = self.scryfall_dict['set']
        self.version_key = f'{self.set_code}_{self.finish[0]}'

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


        # set salt score
        self.set_salt_score()

        # combine sides and list card types
        if self.two_sided:
            self.combine_sides()
        self.set_types()

        # set cm_price
        if not hasattr(self, 'cm_price'):
            self.cm_price = None
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
        try:
            edhrec_data = requests.get(url).json()
            if 'redirect' in edhrec_data and len(edhrec_data) < 3:
                url = f'https://json.edhrec.com/pages{edhrec_data["redirect"]}.json'
                edhrec_data = requests.get(url).json()
        except:
            #print('Error getting Data', self.name)
            salt = 0
        try:
            salt = edhrec_data['container']['json_dict']['card']['salt']
        except:
            #print('no salt score found for ', self.name)
            salt = 0

        self.salt = salt

    def print(self):
        print('Name: ', self.name)
        if hasattr(self, 'mana_cost'):
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

    def to_dict(self, save_to_memory_attributes, save_to_collection_attributes):
        return_dict = {}
        version_dict = {}

        for attribute in self.__dict__:
            attribute_name = attribute.split('_side_')[0]
            if attribute_name in attribute_dict and ((save_to_memory_attributes and attribute_dict[attribute_name][3]) or (save_to_collection_attributes and attribute_dict[attribute_name][4])):
                if attribute_dict[attribute_name][5]:
                    version_dict[attribute] = getattr(self, attribute)
                else:
                    return_dict[attribute] = getattr(self, attribute)


        return return_dict, version_dict

    def save_to_memory(self):
        dicts = self.to_dict(True, False)
        version = dicts[1]
        card = dicts[0]
        if self.key in get_data(filename='memory.json')['cards']:
            set_value(filename='memory.json', dict_path=['cards', self.key, 'versions', self.version_key], value=version)
        else:
            card['versions'] = {}
            card['versions'][self.version_key] = version
            set_value(filename='memory.json', dict_path=['cards', self.key], value=card)
    def add_to_collection(self, subfolder = 'main'):
        dicts = self.to_dict(False, True)
        version = dicts[1]
        card = dicts[0]
        data = get_data(filename='collection.json')[subfolder]
        if subfolder not in data or self.key not in data[subfolder]:
            card['versions'] = {}
            card['versions'][self.version_key] = version
            set_value(filename='collection.json', dict_path=[subfolder, self.key],
                      value=card)
        elif self.version_key not in data[subfolder][self.key]['versions']:
            set_value(filename='collection.json', dict_path=[self.key, 'versions', self.version_key], value=version)
        else:
            increment_value_by(filename='collection.json', dict_path=[self.key, 'versions', self.version_key, 'number'], increment_value=version['number'])