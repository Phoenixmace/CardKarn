from util.json_util import dump_data, get_data
from random import randint
import time
from util.database.sql_card_operations import get_all_cards_by_query
from models.Card import BaseCard

def data_preparation_1():
    data = get_data('small.json', ['machine_learning', 'training_data'])

    # card synergies
    card_synergy_data = data['card_data']
    card_synergies = prepare_direct_card_synergy(card_synergy_data)
    id_synergy_data = get_data('training_id_data_1.json', ['machine_learning', 'synergy_id_list'])
    id_synergy_data['cards'] = card_synergies



def prepare_direct_card_synergy(card_synergy_data):
    formatted_synergies = []
    total_cards = len(card_synergy_data)
    current_card_index = 0
    name_to_id_dict = get_data('name_to_id.json', ['database'])
    card_1_done = []

    for card_1, card_1_data in card_synergy_data.items():
        card_1_data = card_1_data
        print(f'preparing direct_card_synergies: {current_card_index/total_cards*100:.2f}%')

        # get card 1 id
        if card_1 in name_to_id_dict:
            card_1_id = name_to_id_dict[card_1]
        else:
            card_1_item = BaseCard({'name': card_1})
            card_1_id = card_1_item.id

        total_card_1_decks = card_1_data['total']['total']
        card_1_done.append(card_1)
        synergy_list = []

        # calculate all needed synergies
        for card_2, card_2_data in card_1_data['pairing'].items():
            if card_2 not in card_1_done:
                total_card_2_usage = card_2_data['total']
                synergy = total_card_2_usage/total_card_1_decks
                synergy_list.append([card_2, synergy])

        # convert to id and add
        chunk_size = 500
        queries = []
        current_params = ()
        current_card_query = []

        # get needed id's
        for synergy in synergy_list:
            card_synergy = synergy[1]
            card_name = synergy[0]
            if card_name not in name_to_id_dict:
                current_card_query.append('(rowid IN (SELECT rowid FROM cards WHERE (name=? OR (name LIKE ? OR name LIKE ?)) LIMIT 1))')
                current_params = current_params + (card_name, f'{card_name}_//%', f'%//_{card_name}')
            if len(current_card_query) > chunk_size:
                queries.append([current_params, current_card_query])
                current_card_query = []
                current_params = ()
        queries.append([current_params, current_card_query])

        # get the id's
        if len(queries) > 0:
            start = time.time()
            for query in queries:
                one_iteration_start = time.time()
                query_string = ' OR '.join(query[1])
                query_string = 'select scryfall_id, name from cards where ' + query_string
                cards = get_all_cards_by_query(query_string, query[0])
                for card in cards:
                    name_to_id_dict[card[1]] = card[0]
                    if ' // ' in card[1]:
                        for name in card[1].split(' // '):
                            name_to_id_dict[name] = card[0]
                print(f'One iteration with chunk size {len(query[0])/3}: {time.time() - one_iteration_start}:  {(time.time()-one_iteration_start)/len(query[0])/3}s/item')
            print(time.time()-start)

        # add synergies
        for synergy in synergy_list:
            card_synergy = synergy[1]
            card_name = synergy[0]
            if card_name in name_to_id_dict:
                formatted_synergies.append([name_to_id_dict[card_name], card_1_id,card_synergy])

        current_card_index += 1
    dump_data('name_to_id.json', name_to_id_dict, ['database'])
    return formatted_synergies

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



data_preparation_1()

