from mtg.card_class import Card
from mtg.data_management import get_data, dump_data
import requests
import threading
from threading import Thread
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
            print('deck loaded')
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
        if self.format == 'commander' and card_name == self.commander_name:
            return
        card = Card(card_name, set_code=set_code, number=quantity, foil=foil)
        in_list = False
        if hasattr(card, 'mana_cost'):
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
        stats = dict()
        cmc_total = 0
        cmc_cards = 0
        total_cards = 0
        creature_types = dict()
        main_types = dict()
        pips = {
            'B' : 0,
            'U' : 0,
            'G' : 0,
            'R': 0,
            'W': 0,
            'Generic': 0
        }

        # average cmc
        for card in self.decklist:
            if card.double_faced is not True:
                if card.cmc != 0 :
                    cmc_total += card.cmc*card.number
                    cmc_cards += card.number

            # main types
                for type in card.main_types:
                    if type in main_types:
                        main_types[type] += card.number
                    else:
                        main_types[type] = card.number


            # price
                if 'price' not in stats:
                    stats['price'] = 0
                if 'Basic' not in card.supertypes:
                    if hasattr(card, 'cm_price'):
                        stats['price'] += float(card.cm_price)*card.number
                    else:
                        print(f'no price for {card.name} found')

            # number of cards
                total_cards += card.number


            # pips
                for key in pips:
                    if key != 'Generic':
                        pips[key] += card.mana_cost.count(str('{'+key+'}'))*card.number
            # generic
                index = 1
                generic = ''
                while index < len(card.mana_cost) and card.mana_cost[index].isnumeric():
                    generic = generic + card.mana_cost[index]
                    index += 1
                if len(generic) > 0:
                    if 'Generic' in pips:
                        pips['Generic'] += int(generic)
                    else:
                        pips['Generic'] = int(generic)

            # creature types
                if 'Creature' in card.main_types:
                    for type in card.subtypes:
                        if type not in creature_types:
                            creature_types[type] = card.number
                        else:
                            creature_types[type] += card.number

        # define open vars
        if cmc_cards >0:
            stats['avg_cmc'] = cmc_total / cmc_cards

        stats['total_cards'] = total_cards
        stats['total_pips'] = pips
        stats['creature_types'] = creature_types
        stats['main_types'] = main_types
        return stats

    def check_legality(self):
        #Commander
        if 'commander' in self.format:
            if self.commander:
                colors = self.commander.color_identity
            else:
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
            print('woked')
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
                    print(args[key], end= '  |  ')
                print(set)
                self.add_card(**args)
                print(i[index+1:], 'was added')

    def _get_edhrec_data_(self):
        if not self.commander_name:
            print('Please specify your Commander')
            return
        cleaned_name = self.commander_name.lower()
        cleaned_name = cleaned_name.replace(' ', '-')
        to_delete = [',']
        for i in to_delete:
            cleaned_name = cleaned_name.replace(i, '')
        url = f'https://json.edhrec.com/pages/commanders/{cleaned_name}.json'
        try:
            data = requests.get(url).json()
        except:
            print('Error getting Data')
            return
        usable_data = dict()
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


    def _get_all_cards_for_building_(self, load):
        cardlist = {}
        data = self._get_edhrec_data_()
        n_cards = 0
        curr_count = 1
        #add cards from data
        deck_data = get_data('deckbuilding_data')

        if load and self.commander_name in deck_data:
            cardlist['to_buy'] = deck_data[self.commander_name]['to_buy']
            #cardlist['owned'] = deck_data[self.commander_name]['owned']
        else:
            if load and self.commander_name not in deck_data:
                deck_data[self.commander_name] = {}
            for tag in data['recommended_cards']:
                n_cards += len(data['recommended_cards'][tag])
            for tag in data['recommended_cards']:
                for card in data['recommended_cards'][tag]:
                    print(f'Importing suggested cards: {curr_count/n_cards*100}%')
                    tempcard = Card(card)
                    cardlist[card] = {}
                    try:
                        cardlist[card]['salt'] = tempcard.salt
                    except:
                        cardlist[card]['salt'] = None
                    cardlist[card]['synergy'] = data['recommended_cards'][tag][card]['synergy']
                    cardlist[card]['owned'] = False #change if in bulk
                    try:
                        cardlist[card]['cmc'] = tempcard.cmc
                    except:
                        cardlist[card]['cmc'] = None
                        print('card_cmc', tempcard.name)
                    try:
                        cardlist[card]['price'] = tempcard.cm_price
                    except:
                        cardlist[card]['price'] = None
                    try:
                        cardlist[card]['types'] = tempcard.main_types #list

                    except:
                        cardlist[card]['types'] = None #list
                    try:
                        cardlist[card]['rank'] = tempcard.edhrec_rank
                    except:
                        cardlist[card]['rank'] = tempcard.edhrec_rank
                    cardlist[card]['tag'] = tag
                    del tempcard
                    curr_count+=1

        if self.commander in deck_data and len(deck_data[self.commander_name])>1:
            bulkdata = get_data()['bulk']
            commander_colors = self.commander.color_identity
            unusable_list  = ['token', 'emblem', 'planar', 'double_faced_token']
            # get owned cards

            n_cards = 0
            curr_count = 0
            for subfolder in bulkdata:
                for card in bulkdata[subfolder]:
                    n_cards +=1
            print(n_cards)
            for subfolder in bulkdata:
                for card in bulkdata[subfolder]:
                    card = bulkdata[subfolder][card]
                    try:
                        curr_count +=1
                        print(f'iterating over bulk ({curr_count/n_cards*100}%)')
                        print(card['name'])
                        if card['legality']['commander'] == 'legal' and card['layout'] not in unusable_list:
                            legal = True
                            for color in card['color_identity']:
                                if color not in commander_colors:
                                    legal = False
                        if legal:
                            if card['name'] in cardlist:
                                cardlist[card['name']]['owned'] = True
                            else:
                                tempcard = Card(card['name'])
                                cardlist[tempcard.name] = {}
                                try:
                                    cardlist[tempcard.name]['salt'] = tempcard.salt
                                except:
                                    cardlist[tempcard.name]['salt'] = None
                                cardlist[tempcard.name]['synergy'] = None
                                cardlist[tempcard.name]['owned'] = True  # change if in bulk
                                cardlist[tempcard.name]['cmc'] = tempcard.cmc
                                try:
                                    cardlist[tempcard.name]['price'] = tempcard.cm_price
                                except:
                                    cardlist[tempcard.name]['price'] = None
                                try:
                                    cardlist[tempcard.name]['types'] = tempcard.main_types  # list
                                except:
                                    cardlist[tempcard.name]['types'] = []
                                    print(tempcard.name)
                                try:
                                    cardlist[tempcard.name]['rank'] = tempcard.edhrec_rank
                                except:
                                    cardlist[tempcard.name]['rank'] = None
                                del tempcard
                    except:
                        print(f'Problem Loading {card}')
                    del data
        dump_data(deck_data, file_path='deckbuilding_data')
        print(deck_data)
        del deck_data
        return cardlist
    def generate_deck(self, budget, synergy_weight=1, salt_weight=1, rank_weight=-0.5, price_weight=0.2, load=False):

        cardlist = self._get_all_cards_for_building_(load)
        for card_name in cardlist:
            card = cardlist[card_name]
            scores = self._get_card_score_to_build_(card, synergy_weight, salt_weight, rank_weight, price_weight)
            relative_score = scores[1]
            absolute_score = scores[0]
            return_message = scores[2]
            if len(return_message)>1:
                print('the following Attributes for ', card_name, 'were not found:', return_message)
            cardlist[card_name]['absolute_score'] = absolute_score
            cardlist[card_name]['relative_score'] = relative_score
        #cardlist = dict(sorted(cardlist.items(), key=lambda item: item[1]['owned'], reverse=False))
        to_buy = {}
        owned = {}
        for card in cardlist:
            if not cardlist[card]['owned']:
                to_buy[card] = cardlist[card]
            else:
                owned[card] = cardlist[card]
            to_buy = dict(sorted(to_buy.items(), key=lambda item: item[1]['relative_score'], reverse=False))
        for card in to_buy:
            print(card, to_buy[card]['relative_score'], to_buy[card]['rank'], to_buy[card]['salt'], to_buy[card]['synergy'])
        # save for testing
        data = get_data('deckbuilding_data')
        print(data)
        data[self.commander_name] = {}
        data[self.commander_name]['owned'] = owned
        data[self.commander_name]['to_buy'] = to_buy
        print(data)
        dump_data(data, 'deckbuilding_data')
    def _get_card_score_to_build_(self, card:dict, synergy_weight, salt_weight, rank_weight, price_weight): # returns absolute score and /eur
        attributes = ['salt', 'rank', 'price', 'synergy']
        default_values = {'salt': 0, 'rank': 30000, 'price': float('inf'), 'synergy': 0.0}  # Define sensible defaults

        # Ensure all attributes are present in the card
        for attribute in attributes:
            if attribute not in card:
                card[attribute] = default_values[attribute]

        # Extract attributes
        salt = card['salt']  # Community-based rating (0-4)
        rank = card['rank']  # The rank of the card by EDHRec
        price = card['price']
        synergy = card['synergy'] # difference between general usage and specific usage for this certain commander (-1, 1)

        return_message = f''

        if not salt:
            salt = 0
            return_message = return_message+' salt score'
        if not rank:
            rank = 30000
            return_message = return_message+' EDHRec rank'

        normalized_salt = (salt-(0))/4-(1)
        weighted_salt = normalized_salt*salt_weight

        if synergy:
            synergy += 0.3
            normalized_synergy = (synergy-(-1))/1-(-1)
            weighted_synergy = normalized_synergy* synergy_weight
        else:
            weighted_synergy = 0



        owned = card['owned']
        normalized_rank = (rank - (1)) / 30000 - 1
        weighted_rank = normalized_rank * rank_weight

        absolute_score = weighted_salt + weighted_synergy + weighted_rank
        if not owned and price:
            relative_score = absolute_score/(float(price)+1.7)*price_weight
        elif not owned and not price:
            relative_score = absolute_score/10
            print(f'no price for {card['name']}')
        else:
            relative_score = None
        # generate return massage


        return absolute_score, relative_score, return_message
    #def add_card_to_generatingdata(self, card):
