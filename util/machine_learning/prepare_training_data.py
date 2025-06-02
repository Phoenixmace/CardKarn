from util.json_util import dump_data, get_data
from random import randint
import time
from util.database.sql_card_operations import get_all_cards_by_query
from models.Card import BaseCard

def data_preparation_1():
    data = get_data('small_cards.json', ['machine_learning', 'training_data'])

    # card synergies
    card_synergy_data = data['card_data']
    card_synergies = prepare_direct_card_synergy(card_synergy_data)
    id_synergy_data = get_data('small_training_data_1.json', ['machine_learning', 'synergy_id_list'])
    id_synergy_data['cards'] = card_synergies
    dump_data('small_training_data_1.json', id_synergy_data, ['machine_learning', 'synergy_id_list'])
    del data

    # commander
    data = get_data('small_commander.json', ['machine_learning', 'training_data'])
    commander_synergy_data = data['commander_data']
    commander_synergies = prepare_commander_synergy(commander_synergy_data)
    id_synergy_data['commanders'] = commander_synergies
    dump_data('small_training_data_1.json', id_synergy_data, ['machine_learning', 'synergy_id_list'])


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
        if len(current_card_query) > 0:
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

def prepare_commander_synergy(commander_synergy_data):
    name_to_id_dict = get_data('name_to_id.json', ['database'])
    commander_synergies = []
    current_index = 0#[tag, commander_id, card_id]
    total_number = len(commander_synergy_data)

    for commander, commander_data in commander_synergy_data.items():
        commander_total_decks = commander_data['total']
        # get commander id
        if commander in name_to_id_dict:
            commander_id = name_to_id_dict[commander]
        else:
            commander_item = BaseCard({'name': commander})
            commander_id = commander_item.id
            name_to_id_dict[commander] = commander_id
            del commander_item

        # iteration over cards
        synergies = [] # tag, cardname, synergy
        for card, card_data in commander_data['cards'].items():
            for tag, value in card_data.items():
                synergies.append([tag, card, value/commander_total_decks[tag]])

        # get needed id's
        chunk_size = 500
        queries = []
        current_params = ()
        current_card_query = []
        last_card_name = ''
        for synergy in synergies:
            card_name = synergy[1]
            if card_name not in name_to_id_dict and card_name != last_card_name:
                current_card_query.append('(rowid IN (SELECT rowid FROM cards WHERE (name=? OR (name LIKE ? OR name LIKE ?)) LIMIT 1))')
                current_params = current_params + (card_name, f'{card_name}_//%', f'%//_{card_name}')
                if len(current_card_query) > chunk_size:
                    queries.append([current_params, current_card_query])
            last_card_name = card_name
        if len(current_card_query) > 0:
            queries.append([current_params, current_card_query])

        # get id's
        if len(queries) > 0:
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
                print(f'One commander iteration with chunk size {len(query[0])/3}: {time.time() - one_iteration_start}:  {(time.time()-one_iteration_start)/len(query[0])/3}s/item')

        # add synergies
        for synergy in synergies:
            synergy_list = [synergy[0], commander_id, name_to_id_dict[synergy[1].split(' // ')[0]], synergy[2]]
            commander_synergies.append(synergy_list)


        current_index += 1
        print(f'preparing commander_synergies: {round(current_index/total_number, 2)}%')
    dump_data('name_to_id.json', name_to_id_dict, ['database'])
    return commander_synergies




data_preparation_1()

