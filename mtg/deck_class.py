from mtg.card_class import Card
from mtg.data_management import get_data, dump_data
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
                self.commander_name = commander
                self.commander = Card(commander)

    def save(self):
        data = get_data()
        data['decks'][self.name] = self.to_dict()
        dump_data(data)

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

    def check_owned(self): #does not take other verions in considaration
        cards_missing=[] #[name, amount missing]
        data = get_data()
        for card in self.decklist:
            found = False
            #check bulk
            for sub in data['bulk']:
                if sub != 'memory':
                    if card.key in data['bulk'][sub]:
                        if data['bulk'][sub][card.key]['number'] < card.number:
                            found = True
                            cards_missing.append([card.name, card.number-data['bulk'][sub][card.key]['number']])
            if not found:
                cards_missing.append([card.name, card.number])
        if len(cards_missing) > 0:
            print('You are missing:')
            for card in cards_missing:
                print(f'    {card[1]} {card[0]}')

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
