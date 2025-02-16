from xml.sax.saxutils import escape

import scrython
import json
from mtg.data_management import get_data, dump_data
import requests
# what if wrong set/name code
# setattr make sure all attributes are named the same wether loaded or not
# make other lists than main first man

'''
- memory load wthout set code
- foil
'''

class Card():
    def __init__(self, name, number=1, set_code=None, foil=False, language='eng', just_use_cheapest=False):
        self.name = name
        self.language = language
        self.set_code = set_code
        self.number = number
        self.foil = foil
        data = get_data()
        self.key = self.name
        self.key = self.key.lower().replace(' ', '_')
        found = False
        for subfolder in data['bulk']:
            if self.key in data['bulk'][subfolder]:
                print(f'{self.name} loaded')
                if not self.set_code: #maybe take cheapest
                    dict = data['bulk'][subfolder][self.key]['versions']
                    first_key = next(iter(dict))
                    self.version_key = first_key
                    self.set_code = first_key[:-2]
                self.load_g('bulk', subfolder)
                found = True
        if found == False and self.key in data['memory']:
            print('loaded')
            if not self.set_code:
                dict  = data['memory'][self.key]['versions']
                first_key = next(iter(dict))
                self.version_key = first_key
                self.set_code = first_key[:-2]
            self.load_g('memory')
        if not found:
            if not self.set_scryfall_att():
                print(f"Failed to initialize Card: {self.name}")
                del self  # Break local reference in the constructor
                return
            try:
                self.set_salt_score()
            except:
                print(f'There was an Error while retrieving the Salt score with {self.name}')
                self.salt = None
            self.save_to('memory')
        self.key = str(self.name)
        self.key = self.key.lower().replace(' ', '_')
        self.number = number
        self.foil = foil


    def set_scryfall_att(self):
        search_params = {'fuzzy':self.name}
        if self.set_code:
            search_params['set'] = self.set_code
        # searches based on given params
        try:
            self.scryfall_data = scrython.cards.Named(**search_params)
            print('made request')
            print(self.key)
        except:
            print(f'{self.name} not found')
            return False
        # if not exactly the same
        if self.scryfall_data.name().lower() != self.name.lower():
            print(f'{self.name} was not found. Instead proceeded with: {self.scryfall_data.name()}')
        self.name = self.scryfall_data.name()
        # Two faced
        self.layout = self.scryfall_data.layout()
        self.cm_price = self.scryfall_data.prices('eur')
        if not self.cm_price:
            self.cm_price = None
        self.set_code = self.scryfall_data.set_code()
        self.typeline = self.scryfall_data.type_line()
        self.legality = self.scryfall_data.legalities()
        self.color_identity = self.scryfall_data.color_identity()
        self.cmc = self.scryfall_data.cmc()
        self.image_uris = self.scryfall_data.image_uris()
        print(self.image_uris)
        try:
            self.edhrec_rank = self.scryfall_data.edhrec_rank()
        except:
            self.edhrec_rank = None
        normal_layouts = ['normal', 'class', 'case', 'saga']
        unusable_layouts = ['planar', 'token', 'emblem', 'double_faced_token']
        if self.layout in unusable_layouts:
            print(f'{self.name} skipped because of unusable layout')
            return False
        elif self.layout not in normal_layouts:
            self.side_1 = {}
            self.side_2 = {}
            self.supertypes = self.get_supertypes(self.typeline)
            self.subtypes = self.get_subtypes(self.typeline)
            self.main_types = self.get_maintypes(self.typeline)
            self.set_remaining_attributes(1)
            self.set_remaining_attributes(2)

        else: # normal
            self.set_remaining_attributes()
        return True

    def set_remaining_attributes(self, side=None):
        data_to_fetch = {
            'name':'name',
            'ruling':'oracle_text',
            'mana_cost':'mana_cost',
            'typeline':'type_line'
        }

        if side:
            try:
                data = self.scryfall_data.card_faces()[side-1]
            except:
                print(self.name, self.layout)
            side_dict = {}
        else:
            data = self.scryfall_data.__dict__['scryfallJson']

        for i in data_to_fetch:
            attribute_value = data[data_to_fetch[i]]
            if side:

                side_dict[i] = attribute_value
            else:
                setattr(self, i, attribute_value)
        typeline = data['type_line']
        subtypes = self.get_subtypes(typeline)
        supertypes = self.get_supertypes(typeline)
        maintypes = self.get_maintypes(typeline)
        if side:
            side_dict['subtypes'] = subtypes
        else:
            setattr(self, 'subtypes', subtypes)
        # Supertypes
        if side:
            side_dict['supertypes'] = supertypes
        else:
            setattr(self, 'supertypes', supertypes)

        # Main types
        if side:
            side_dict['maintypes'] = maintypes
        else:
            setattr(self, 'main_types', maintypes)

        if 'Creature' in maintypes:
            power = data['power']
            toughness = data['toughness']
            if side:
                side_dict['power'] = power
                side_dict['toughness'] = toughness
            else:
                setattr(self, 'power', power)
                setattr(self, 'toughness', toughness)
        if 'Planeswalker' in maintypes:
            loyalty = data['loyalty']
            if side:
                side_dict['loyalty'] = loyalty
            else:
                setattr(self, 'loyalty', loyalty)
        if side:
            self.__setattr__(f'side_{side}', side_dict)
    def set_salt_score(self):
        if self.layout == 'transform':
            index = 0
            name = ''
            while self.name[index] != '/':
                name = name + self.name[index]
                index += 1
            name = name[:-1]
        elif self.layout == 'split':
            name = self.name
            name = name.replace(' // ', '-')
        elif self.layout == 'modal_dfc':
            name = self.side_1['name']
        else:
            name = self.name

        cleaned_name = name.lower()
        cleaned_name = cleaned_name.replace(' ', '-')
        cleaned_name = cleaned_name.replace('ó', 'o')
        to_delete = [',', '\'']
        for i in to_delete:
            cleaned_name = cleaned_name.replace(i, '')
        url = f'https://json.edhrec.com/pages/cards/{cleaned_name}.json'
        try:
            edhrec_data = requests.get(url).json()
        except:
            print('Error getting Data')
            return
        salt = edhrec_data['container']['json_dict']['card']['salt']
        self.salt = salt
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

    def save_to(self, main_folder='bulk', subfolder=None, del_after_save=False):
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
        if del_after_save:
            del self

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


