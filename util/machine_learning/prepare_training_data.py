from util.json_util import dump_data, get_data
from random import randint
from util.database.sql_card_operations import get_all_cards_by_query
from models.Card import BaseCard

def data_preparation_1():
    data = get_data('full_import.json', ['machine_learning', 'training_data'])
    item = 0
    total = len(data['card_data'])
    # card synergies
    card_synergy_data = data['card_data']
    card_synergies = get_data('training_card_synergies_1.json', ['machine_learning', 'synergy_id_list'])
    for anchor_card, anchor_data in card_synergy_data.items():
        item +=1
        print(f'{item/total*100:.2f}%')
        # no tags
        total_anchor_decks = anchor_data['total']
        for card, second_data in anchor_data['pairing'].items():
            key = [card, anchor_card]
            key.sort()
            key = '#'.join(key)
            if key not in card_synergies:
                sub_synergy = second_data['total']/(total_anchor_decks['total'])
                card_synergies[key] = sub_synergy
        if item%4000==0 and item!=1:
            print('dumping')
            dump_data('training_card_synergies_1.json', card_synergies, ['machine_learning', 'synergy_id_list'])

    # convert to id
    convert_name_to_id_dict(card_synergies)
    dump_data('training_card_synergies_1.json', card_synergies, ['machine_learning', 'synergy_id_list'])
    # no synergy card adding
    number_of_synergies = len(card_synergies)
    no_synergy_percentage = 10
    all_cards = get_all_cards_by_query(f"select json from cards where commander_legal")
    for i in range(int(no_synergy_percentage/100*number_of_synergies)):
        synergy_already_added = True
        while not synergy_already_added:
            card_1 = BaseCard(card_json=all_cards[randint(0, len(all_cards)-1)])
            card_2 = BaseCard(card_json=all_cards[randint(0, len(all_cards)-1)])
            key = [card_2.id, card_1.id]
            key.sort()
            key = '+'.join(key)
            synergy_already_added = key in card_synergies
        card_synergies[key] = 0

def convert_name_to_id_dict(dict):
    dict = get_data('training_card_synergies_1.json', ['machine_learning', 'synergy_id_list'])
    return_dict = {}
    id_dict = {}
    chunk = []
    chunk_size = 500
    for key in dict:
        key = key.split('#')
        for key in key:
            if key not in id_dict and key not in chunk:
                chunk.append(key)
        # convert
        if len(chunk) > chunk_size:
            query = 'select scryfall_id, name from cards where '
            card_param = '(rowid IN (SELECT rowid FROM cards WHERE (name=? OR (name LIKE ? OR name LIKE ?)) LIMIT 1))'
            params = ()
            for card_name in chunk:
                query = query + card_param
                if card_name != chunk[-1]:
                    query = query + ' OR '
                params = params + (card_name, f'{card_name}_//%', f'%//_{card_name}')
            cards = get_all_cards_by_query(query, params)
            for i in cards:
                id_dict[i[1]] = i[0]
            chunk = []
    for key, value in dict.items():
        key = key.split('#')
        card_1 = id_dict[key[0]]
        card_2 = id_dict[key[1]]
        key = [card_2, card_1]
        key.sort()
        return_dict['#'.join(key)] = value
    return return_dict





convert_name_to_id_dict({})