from mtg.card_class import Card
from mtg.data_management import get_data, dump_data
import requests
import math
'''
methods to add:
    load from text (on PC) add to init
    check owned cards (ignore memory in bulk)
    sideboard
    skip if too many cards in add deck
    mein type stat as dict 
    restricted cards?
'''
# decklist as [[name, set, number, foil]]
class Deck():
    def __init__(self, deck_name, format='commander', decklist=[], commander = None):
        data = get_data()
        if deck_name in data['decks']:
            # print('deck loaded')
            for arg in data['decks'][deck_name]:
                setattr(self, arg, data['decks'][deck_name][arg])
            self.decklist = []
            for card in self.name_list:
                self.import_name(card[0], card[1], card[2], card[3])

        else:
            self.name_list = decklist
            self.format = format
            self.decklist = []
            self.name = deck_name
            if self.format == 'commander':
                self.commander = Card(commander)
                self.commander_name = self.commander.name
        del data
    def save(self):
        data = get_data()
        data['decks'][self.name] = self.to_dict()
        dump_data(data)
        del data

    def to_dict(self):
        return {
            'name_list': self.name_list,
            'commander': self.commander_name,
            'format': self.format,
            'name': self.name,
            'commander_name': self.commander_name
        }

    def add_card(self, card_name, set_code=None, quantity=1, foil=False):
        starting_decklist_length = self.get_stats()['total_cards']
        if self.format == 'commander' and card_name == self.commander_name:
            return
        card = Card(card_name, set_code=set_code, number=quantity, foil=foil)
        in_list = False
        if 1==1:
            for card_in_list in self.name_list:
            # in case the card is already there just add it
                if card_in_list[0] == card.name:
                    in_list = True
                    card_in_list[2] += card.number
            if in_list == True:
                for card_in_list in self.decklist:
                    if card_in_list.name == card.name:
                        card_in_list.number += card.number

            if in_list == False:
                self.decklist.append(card)
                self.name_list.append([card.name, card.set_code, card.number, card.foil])

        if starting_decklist_length == self.get_stats()['total_cards']:
            print(f'Error while adding {card_name} to deck')
    def import_name(self, card_name, card_setcode, card_quantity, card_foil=False):
        args = {
            'name': card_name
        }
        if card_setcode:
            args['set_code'] = card_setcode
        if card_quantity:
            args['number'] = card_quantity
        if card_foil:
            args['foil'] = card_foil
        card = Card(**args)
        self.decklist.append(card)

    def print(self):
        for card in self.decklist:
            print(f'{card.number} {card.name}')

    def get_stats(self):
        # setup dict
        pips = {
            'B': 0,
            'U': 0,
            'G': 0,
            'R': 0,
            'W': 0,
            'C': 0,
        }
        stats = {
            'average_cmc': None,
            'mana_curve': dict(),
            'pips': None,
            'producer': pips,
            'total_cards': 0,
            'card_types': dict(),
            'creature_types': dict(),
            'price': 0
                 }
        pips['generic'] = 0
        stats['pips'] = pips
        cmc_total = 0

        for card in self.decklist:
            # add to total cards
            stats['total_cards'] += card.number
            cmc_total += card.number*card.cmc

            # Mana Curve
            if 'Land' not in card.main_types:
                if str(int(card.cmc)) not in stats['mana_curve']:
                    stats['mana_curve'][str(int(card.cmc))] = int(card.cmc*card.number)
                else:
                    stats['mana_curve'][str(int(card.cmc))] += int(card.cmc * card.number)

            # card types
            for type in card.main_types:
                if type in stats['card_types']:
                    stats['card_types'][type] += card.number
                else:
                    stats['card_types'][type] = card.number


            # price
            if 'Basic' not in card.supertypes:
                if hasattr(card, 'cm_price'):
                    stats['price'] += float(card.cm_price)*card.number
                else:
                    pass
                    # print(f'no price for {card.name} found')



            # pips
                if hasattr(card, 'mana_cost'):
                    for key in pips:
                        if key != 'generic':
                            stats['pips'][key] += card.mana_cost.count(str('{'+key+'}'))*card.number
                # generic
                    index = 1
                    generic = ''
                    while index < len(card.mana_cost) and card.mana_cost[index].isnumeric():
                        generic = generic + card.mana_cost[index]
                        index += 1
                    if len(generic) > 0:
                        stats['pips']['generic'] += int(generic)*card.number
            # Producer
            # creature types
            if 'Creature' in card.main_types:
                for subtype in card.subtypes:
                    if subtype not in stats['creature_types']:
                        stats['creature_types'][subtype] = card.number
                    else:
                        stats['creature_types'][subtype] = card.number



        return stats

    def check_legality(self):
        #Commander
        if 'commander' in self.format:
            if self.commander:
                colors = self.commander.color_identity
            else:
                pass
                print('no commander found')
            if 'Legendary' not in self.commander.typeline and 'Creature' not in self.commander.typeline:
                print('The Commander must be a legendary Creature')
                return False
            for card in self.decklist:
                if 'Basic' not in card.supertypes:
                    if card.number > 1: # excepions like Nazgul not included
                        return False
                    for color in card.color_identity:
                        if color not in colors:
                            print(f'{card.name} has {color} in its color identity')
                            return False
                    if card.legality[self.format] != 'legal':
                        print(f'{card.name} is not legal in ', self.format)
                        return False
                if self.get_stats()['total_cards'] != 99: #revert after testing
                    print('The deck must have 99 cards')
                    return False
        else:
            for card in self.decklist:
                if 'Basic' not in card.supertypes:
                    if card.number > 4:  # excepions like Nazgul not included
                        print(f'{card.name} is {card.number} times in the Deck')
                        return False
                if card.legality[self.format] != 'legal' and card.legality[self.format] != 'restricted': #find out what restricted is
                    print(f'{card.name} is not legal in ', self.format)
                    return False
            if self.get_stats()['total_cards'] < 60:  # revert after testing
                print('The deck must have 60 cards')
                return False
        return True

    def delete_card(self, name, amount):
        for index, card in enumerate(self.decklist):
            if card.name.lower() == name.lower():
                card.number -= amount
                if card.number < 1:
                    del self.decklist[index]
                return
        print(f'{name} was not found in deck')

    def delete(self):
        if  input('Do you really want to delete this deck? y/n').lower() == 'y':
            data = get_data()
            del data['decks'][self.name]
            dump_data(data)
            del data

    def check_owned(self): #does not take other verions in considaration
        cards_missing=[] #[name, amount missing]
        data = get_data()
        for card in self.decklist:
            found = False
            #check bulk
            for sub in data['bulk']:
                if card.key in data['bulk'][sub]:
                    # get sum of all cards
                    sum = 0
                    for version in data['bulk'][sub][card.key]['versions']:
                        sum += data['bulk'][sub][card.key]['versions'][version]['number']
            if sum < card.number:
                found = True
                cards_missing.append([card.name, card.number- sum])
            if not found:
                cards_missing.append([card.name, card.number])
        if len(cards_missing) > 0:
            print('You are missing:')
            for card in cards_missing:
                print(f'    {card[1]} {card[0]}')
        del data
    def import_deck(self, list=None): # 3 Hedron Crab  format
        if not list:
            list = input()
        for i in list.split('\n'):
            if len(i) > 1:
                index = 0
                num = ''
                args = dict()

                #num
                while index < len(i) - 1 and i[index] != ' ':
                    num += i[index]
                    index += 1
                try:
                    args['quantity'] = int(num)
                except:
                    args['quantity'] = 1
                    print('number error with', i)
                if '(' in i:
                    set = i[i.find('(')+1:i.find(')')]
                    args['set_code'] = set
                    args['card_name'] = i[index + 1:i.find('(')-1]
                else:
                    args['card_name'] = i[index + 1:]

                for key in args:
                    pass
                    # print(args[key], end= '  |  ')
                # print(set)
                self.add_card(**args)
                # print(i[index+1:], 'was added')

    def _get_edhrec_data_(self, price_class=False):
        if not self.commander_name:
            print('Please specify your Commander')
            return
        usable_data = dict()
        cleaned_name = self.commander_name.lower()
        cleaned_name = cleaned_name.replace(' ', '-')
        to_delete = [',']
        for i in to_delete:
            cleaned_name = cleaned_name.replace(i, '')
        url = f'https://json.edhrec.com/pages/commanders/{cleaned_name}'
        if price_class:
            url += f'/{price_class}'
        url += '.json'
        try:
            data = requests.get(url).json()
        except:
            # print('Error getting Data')
            return
        # get combos
        if 'combocounts' in data['panels']:
            usable_data['combos'] = {}
            combos = data['panels']['combocounts']
            combo_number = 0
            for combo in combos:
                combo_number += 1
                combo_string = combo['value']
                combo_string = combo_string.split(' + ')
                if len(combo_string) > 1:
                    usable_data['combos'][combo_number] = None
                    combo_piece_list = []
                    for combo_piece in combo_string[1:]:
                        combo_piece_list.append(combo_piece)
                    usable_data['combos'][combo_number] = combo_piece_list
        else:
            usable_data['combos'] = None


        usable_data['mana_curve'] = data['panels']['mana_curve']
        usable_data['recommended_cards'] = dict()
        usable_data['creatures'] = data['creature']
        usable_data['battles'] = data['battle']
        usable_data['instants'] = data['instant']
        usable_data['sorceries'] = data['sorcery']
        usable_data['lands'] = data['land']
        usable_data['basics'] = data['basic']
        usable_data['planeswalker'] = data['planeswalker']
        usable_data['nonbasics'] = data['nonbasic']
        usable_data['enchantments'] = data['enchantment']
        usable_data['artifacts'] = data['artifact']
        usable_data['commander_salt'] = data['container']['json_dict']['card']['salt']
        for i in data['container']['json_dict']['cardlists']:
            usable_data['recommended_cards'][i['tag']] = dict()
            for card in i['cardviews']:
                name = card['name']
                usable_data['recommended_cards'][i['tag']][name] = dict()
                usable_data['recommended_cards'][i['tag']][name]['synergy'] = card['synergy']
        return usable_data



    def generate_deck(self, budget, synergy_weight=1.8, salt_weight=1.5, rank_weight=0.8, price_penalty_weight = 0.35, load=False): #price as an exponent
        # convert synergys to dict
        self.generated_decklist = {}
        weights = {
            'synergy': synergy_weight,
            'salt': salt_weight,
            'edhrec_rank': rank_weight,
            'price_penalty_weight': price_penalty_weight
        }


        card_data  = self._get_building_data(load, weights, budget)

        # prepare owned
        owned =card_data[0]
        owned = dict(sorted(owned.items(), key=lambda item: item[1]['absolute'], reverse=True))
        for key in owned:
            owned[key]['relative'] = owned[key]['absolute']

        to_buy = card_data[1]
        edhrec_data = card_data[2]
        mana_curve = edhrec_data['mana_curve']

        # prepare all
        all_cards = to_buy
        for key in owned:
            all_cards[key] = owned[key]
        try:
            del all_cards[self.commander.key]
        except:
            pass
        all_cards = dict(sorted(to_buy.items(), key=lambda item: item[1]['relative'], reverse=True))


        for i in range(20):
            if str(i) not in mana_curve:
                mana_curve[str(i)] = 0



        current_mana_distribution = {}
        for i in range(20):
            current_mana_distribution[str(i)] = 0
        # add_basics


        type_distribution = {
            'Instant':edhrec_data['instants'],
            'Sorcery':edhrec_data['sorceries'],
            'Creature':edhrec_data['creatures'],
            'Artifact':edhrec_data['artifacts'],
            'Enchantment':edhrec_data['enchantments'],
            'Battle':edhrec_data['battles'],
            'Planeswalker':edhrec_data['planeswalker'],
            'Land':edhrec_data['lands']-edhrec_data['basics']
                             }

        current_distribution = {
            'Instant':0,
            'Sorcery':0,
            'Creature':0,
            'Artifact':0,
            'Enchantment':0,
            'Battle':0,
            'Planeswalker':0,
            'Land':0
                             }
        basic_lands = [
            "plains",
            "island",
            "swamp",
            "mountain",
            "forest",
            "snow-covered plains",
            "snow-covered island",
            "snow-covered swamp",
            "snow-covered mountain",
            "snow-covered forest",
            "wastes"
        ]

        budget_used = 0

        temp_buylist = []

        # add all cards
        for card in all_cards:
            card_dict = all_cards[card]
            # check if owned
            card_is_owned = False
            if card in owned:
                card_is_owned = True
            try:
                card_dict['cm_price'] = float(card_dict['cm_price'])
            except:
                card_dict['cm_price'] = False


            if (card_dict['cm_price'] or card_is_owned) and (card_is_owned or card_dict['cm_price']+ 1.7 +budget_used < budget) and (current_distribution[card_dict['main_types'][0]] < type_distribution[card_dict['main_types'][0]]) and ((current_mana_distribution[str(int(card_dict['cmc']))]-3< mana_curve[str(int(card_dict['cmc']))]) or 'Land' in card_dict['main_types'])  and (len(self.generated_decklist)< 99-edhrec_data['basics']) and (card_dict['name'].lower() not in basic_lands):
                if not card_is_owned:
                    budget_used += card_dict['cm_price'] +1.7
                    temp_buylist.append(card_dict['name'])

                current_distribution[card_dict['main_types'][0]] += 1
                current_mana_distribution[str(int(card_dict['cmc']))] += 1
                self.generated_decklist[card] = card_dict
                self.generated_decklist[card]['number'] = 1
                self.add_card(card_dict['name'])
                #print(card_dict['name'], card_dict['relative'], card_dict['salt'], card_dict['edhrec_rank'], card_dict['synergy'])

        basics_to_add = 99-len(self.generated_decklist)

        basics_added = 0
        basics = {
            'W': 'plains',
            'R': 'mountain',
            'U': 'island',
            'G': 'forest',
            'B': 'swamp',
        }
        basics_distribution = self.get_stats()['pips']
        # ddelete unused colors
        keys_to_delete = []
        for color in basics_distribution:
            if color not in self.commander.color_identity:
                keys_to_delete.append(color)
        for key in keys_to_delete:
            del basics_distribution[key]


        total_pips = 1

        #get total pips
        for pip in basics_distribution:
            total_pips += basics_distribution[pip]

        # evaluate how many
        for pip in basics_distribution:
            basics_distribution[pip] = int(round((basics_distribution[pip]/total_pips*basics_to_add) - (2/len(self.commander.color_identity))))

        # make the basics complete
        # least used color
        least_used_color = False
        for color in basics_distribution:
            if not least_used_color:
                least_used_color = color
            elif basics_distribution[least_used_color] > basics_distribution[color]:
                least_used_color = color
        # how many current basics
        current_basics = 0
        for color in basics_distribution:
            current_basics += basics_distribution[color]

        basics_distribution[least_used_color] +=  basics_to_add-current_basics
        # actually add them
        for color_key in basics_distribution:
            self.generated_decklist[basics[color_key]] = owned[basics[color]]
            self.generated_decklist[basics[color_key]]['number'] = basics_distribution[color_key]
            self.add_card(basics[color_key], quantity=basics_distribution[color_key])
        #print(temp_buylist)







    def _get_building_data(self, load, weights, budget):
        owned = {}
        to_buy = {}
        # set price class

        if budget > 200:
            price_class = 'expensive'
        else:
            price_class = False

        edhrec_data = self._get_edhrec_data_(price_class=price_class)
        # if load is enabled
        if load:
            deckfile_data = get_data('deckbuilding_data')
            if self.commander.key in deckfile_data:

                # check if to buy is there
                if 'to_buy' in deckfile_data[self.commander.key] and len(deckfile_data[self.commander.key]['to_buy']) > 0:
                    to_buy = deckfile_data[self.commander.key]['to_buy']
                #check owned
                if 'owned' in deckfile_data[self.commander.key] and len(deckfile_data[self.commander.key]['owned']) > 0:
                    owned = deckfile_data[self.commander.key]['owned']

        attributes_to_add = ['salt', 'cmc', 'cm_price', 'main_types', 'edhrec_rank', 'name']

        # if no buy
        if len(to_buy) < 1:
            n_edhrec_cards = 0
            curr_count = 1
            #count cards
            for tag in edhrec_data['recommended_cards']:
                for card in edhrec_data['recommended_cards'][tag]:
                    n_edhrec_cards+=1
            for tag in edhrec_data['recommended_cards']:
                for card in edhrec_data['recommended_cards'][tag]:
                    print(f'Importing suggested cards: {curr_count / n_edhrec_cards * 100}%')
                    tempcard = Card(card)
                    card_key = tempcard.key
                    to_buy[card_key] = {}
                    #set Card class atts
                    for attribute in attributes_to_add:
                        try:
                            value = getattr(tempcard, attribute)
                            to_buy[card_key][attribute] = value
                        except:
                            to_buy[card_key][attribute] = None
                            print(f'Error while retrieving {attribute} from {card}')
                    # other atts
                    to_buy[card_key]['synergy'] = edhrec_data['recommended_cards'][tag][card]['synergy']
                    to_buy[card_key]['tag'] = tag
                    del tempcard
                    curr_count += 1

        # if no owned (later Threading
        if len(owned) < 1:
            bulkdata = get_data()['bulk']
            unusable_list  = ['token', 'emblem', 'planar', 'double_faced_token']
            commander_colors = self.commander.color_identity
            n_bulkcards = 0
            curr_count = 1
            # count cards
            for subfolder in bulkdata:
                for card in bulkdata[subfolder]:
                    n_bulkcards +=1

            # add_cards
            for subfolder in bulkdata:
                for card in bulkdata[subfolder]:
                    print(f'Importing suggested cards: {curr_count / n_bulkcards * 100}%', card)
                    card_dict = bulkdata[subfolder][card]
                    legal = True
                    # check legality
                    # layout
                    if 'layout' not in card_dict or card_dict['layout'] in unusable_list:
                        legal = False
                    # legality
                    elif 'legality' not in card_dict or card_dict['legality']['commander'] != 'legal':
                        legal = False
                    else:
                        for color in card_dict['color_identity']:
                            if color not in commander_colors:
                                legal = False


                    if legal:
                        owned[card] = {}
                        # move in case recommended
                        if card in to_buy:
                            # print('you already own', card)
                            owned[card] = to_buy[card]
                            del to_buy[card]
                        else:
                            owned[card]['synergy'] = None

                            for attribute in attributes_to_add:
                                try:
                                    value = card_dict[attribute]
                                    owned[card][attribute] =value
                                except:
                                    owned[card][attribute] = None
                                    print(f'Error while retrieving {attribute} of {card_dict['name']}')

                        # get eval
                        curr_count += 1
                        del card_dict

        # evaluate cards
        # to_buy
        for card in to_buy:
            scores = self._get_card_eval(to_buy[card], weights, budget)
            to_buy[card]['absolute'] = scores[0]
            to_buy[card]['relative'] = scores[1]

        for card in owned:
            scores = self._get_card_eval(owned[card], weights, budget)
            owned[card]['absolute'] = scores[0]

        # save
        data = get_data('deckbuilding_data')
        data[self.commander.key] = {}
        data[self.commander.key]['owned'] = owned
        data[self.commander.key]['to_buy'] = to_buy
        dump_data(data, file_path='deckbuilding_data')
        del data

        # return
        return owned, to_buy, edhrec_data

    def _get_card_eval(self, card, weights, budget):
        default_values = {'salt': 0, 'edhrec_rank': 36108, 'cm_price': 10, 'synergy': 0.0}


        # calculate salt
        if card['salt']:
            weighted_salt = card['salt']/4
            weighted_salt = weighted_salt * weights['salt']
        else:
            weighted_salt = default_values['salt']

        # calculate synergy
        if card['synergy']:
            weighted_synergy = (card['synergy']+1.2)/(2)
            weighted_synergy = weighted_synergy * weights['synergy']
        else:
            weighted_synergy = default_values['synergy']

        # calculate synergy
        if card['edhrec_rank']:
            weighted_edhrec_rank = (36108-card['edhrec_rank']) / (36107)
            weighted_edhrec_rank = weighted_edhrec_rank * weights['edhrec_rank']
        else:
            weighted_edhrec_rank = default_values['edhrec_rank']

        absolute_value = weighted_edhrec_rank + weighted_synergy + weighted_salt

        # define Price
        if card['cm_price'] and type(card['cm_price']) == float:
            price = card['cm_price'] + 1.7
        else:
            price = default_values['cm_price']

        price_penalty = weights['price_penalty_weight']*(math.log10(price) + 1)

        # Budgets scaling factor
        budget_scaling_factor = ((4-math.log10(budget))/4)
        if budget_scaling_factor > 1:
            budget_scaling_factor = 1
        if budget_scaling_factor < 0:
            budget_scaling_factor = 0
        # eval relative value
        price_penalty = price_penalty**budget_scaling_factor

        relative_value = absolute_value / price_penalty
        return absolute_value, relative_value


