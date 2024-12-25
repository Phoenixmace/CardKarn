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
    def __init__(self, name, number=1, set_code=None, foil=False):
        self.name = name
        self.set_code = set_code
        self.number = number
        self.foil = foil
        data = get_data()
        self.key = ((self.name).lower()).replace(' ', '_')
        loaded = False
        for subfolder in data['bulk']:
            if self.key in data['bulk'][subfolder]:
                self.load_g('bulk', 'main')
                loaded = True
        if loaded == False and self.key in data['memory']:
            self.load_g('memory')
        else:
            self.set_scryfall_att()
            self.save_to('memory')
        self.key = ((self.name).lower()).replace(' ', '_')
        self.number = number
        self.foil = foil
        # Necessairy?


    def set_scryfall_att(self):
        search_params = {'fuzzy':self.name}
        if self.set_code:
            search_params['set'] = self.set_code
        # searches based on given params
        try:
            self.scryfall_data = scrython.cards.Named(**search_params)
        except:
            print(f'{self.name} not found')
            return
        # if not exactly the same
        if self.scryfall_data.name().lower() != self.name.lower():
            print(f'{self.name} was not found. Instead proceeded with: {self.scryfall_data.name()}')
        self.name = self.scryfall_data.name()
        # Two faced
        if '//' in self.name:
            self.set_two_face()
            print('This is a double sided card')

        # one face
        else:
            self.double_faced = False
            self.set_code = self.scryfall_data.set_code()
            self.typeline = self.scryfall_data.type_line()
            self.cm_price = self.scryfall_data.prices('eur')
            self.ruling = self.scryfall_data.oracle_text()
            self.legality = self.scryfall_data.legalities()
            self.color_identity = self.scryfall_data.color_identity()
            self.mana_cost = self.scryfall_data.mana_cost()
            self.subtypes = self.get_subtypes(self.typeline)
            self.cmc = self.scryfall_data.cmc()
            #Set supertypes
            self.supertypes = []
            supertypes = ['Legendary', 'Tribal', 'Basic', 'Snow']
            for supertype in supertypes:
                if supertype in self.typeline:
                    self.supertypes.append(supertype)

            #Set Main_types (add battle start)
            self.main_types = []
            main_types = ['Creature', 'Planeswalker', 'Battle', 'Land', 'Artifact', 'Instant', 'Sorcery', 'Enchantment']
            for main_type in main_types:
                if main_type in self.typeline:
                    self.main_types.append(main_type)
                    if main_type == 'Creature':
                        self.power = self.scryfall_data.power()
                        self.toughness = self.scryfall_data.toughness()
                    if main_type == 'Planeswalker':
                        self.loyalty = self.scryfall_data.loyalty()
                    else:
                        self.loyalty = None
        self.set_salt_score()
    def set_salt_score(self):
        cleaned_name = self.name.lower()
        cleaned_name = cleaned_name.replace(' ', '-')
        to_delete = [',']
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


    def set_two_face(self):
        self.double_faced = True
        self.front = self.scryfall_data.card_faces()[0]
        self.back = self.scryfall_data.card_faces()[1]
        self.typeline = self.front['type_line'] + self.back['type_line']

    def get_subtypes(self, typeline):
        subtypes = []
        if '—' in typeline:
            substr = typeline[typeline.index('—')+2:].split(' ')
            for creature_type in substr:
                subtypes.append(creature_type)
            return subtypes
        else:
            return None

    def save_to(self, main_folder='bulk', subfolder=None):
        # Read the existing data from the JSON file
        data = get_data() # get data
        # set setkey
        if self.foil:
            version_key = self.set_code + '_f'
            version_key = (version_key.lower()).replace(' ', '_')
        else:
            version_key = self.set_code + '_n'
            version_key = (version_key.lower()).replace(' ', '_')

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
        save_to_versions = ['set_code', 'foil', 'number', 'cm_price']
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
        if self.set_code and self.foil:
            if self.foil:
                version_key = self.set_code + '_f'
                version_key = (version_key.lower()).replace(' ', '_')
            else:
                version_key = self.set_code + '_n'
                version_key = (version_key.lower()).replace(' ', '_')
        else:
            self.set_scryfall_att()
            return

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
