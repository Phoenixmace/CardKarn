import time
import json
from util.data_util import json_util, data_util
from util.threading_util import ThreadingHandler
import requests
from itertools import combinations
from util.database import sql_card_operations
import threading

def add_all_decks(threads, save_interval, fetched_data_name, number_of_decks):
    threading_handler = ThreadingHandler(threads)
    all_hashes = json_util.get_data('decklist_hashes.json', ['training_data', 'fetched_data', fetched_data_name, 'util_data'])
    name_to_id = json_util.get_data('name_to_id.json', ['training_data', 'fetched_data', fetched_data_name, 'util_data'])
    synergies = json_util.get_data('synergies.json', ['training_data', 'fetched_data', fetched_data_name, 'fetched_data'])
    total_decks = json_util.get_data('total_decks.json', ['training_data', 'fetched_data', fetched_data_name, 'fetched_data'])
    binary_data = json_util.get_data('binary_list.json', ['training_data', 'fetched_data', fetched_data_name, 'fetched_data'])
    lock = threading.Lock()
    if number_of_decks:
        all_hashes = all_hashes[:number_of_decks]
    params = [(hash, name_to_id, binary_data, synergies, total_decks, lock, index%save_interval==0 and index != 0, fetched_data_name) for index, hash in enumerate(all_hashes)]
    threading_handler.start_process(params, add_deck, process_message='Gathering decks')
    return binary_data, synergies, total_decks

def add_deck(hash, name_to_id, binary_data, synergies,total_decks, lock, save_data, dataset_name):
    # get deck data
    url = f'https://edhrec.com/api/deckpreview/{hash}'
    response = requests.get(url,timeout=20)
    if response.status_code == 200:
        data = response.json()
    else:
        print(hash)
        return
    # parse data

    # parsing data
    decklist = data['cards']

    # color
    color_identity = data['coloridentity']
    color_identity.sort()
    color_identity = ''.join(color_identity)


    cedh = data['cedh']

    # tags

    tags = data['tags'] + data['edhrec_tags']
    tribe = data['tribe']

    salt = data['salt']
    if salt:
        salt = int(salt)


    # price
    price = data['price']
    price_categories = {
        price < 1000: 3,
        price < 250: 2,
        price < 100: 1,

    }
    price_category = price_categories.get(True, 4)

    commanders = data['commanders']
    for commander in commanders:
        if commander:
            decklist.append(commander)
    del data

    #convert_to_ids
    id_decklist = [name_to_id[card] for card in decklist if card in name_to_id]
    ids_to_get = [card for card in decklist if card not in name_to_id and ' // ' not in card]
    double_sided_id = [card for card in decklist if card not in name_to_id and ' // ' in card]
    if len(ids_to_get) > 0 or len(double_sided_id) > 0:
        new_ids = convert_names_to_ids(name_to_id, ids_to_get, double_sided_id, lock)
        id_decklist += new_ids

    for combo in combinations(id_decklist, 2):
        combo = list(combo)
        combo.sort()
        combo = tuple(combo)
        add_synergy_to_var(combo, binary_data, synergies, total_decks, lock, price_category, cedh, color_identity, tribe, tags, salt)
    if save_data:
        time_stamp = str(time.time())[:5]
        filepaths = [
            (data_util.get_data_path(f'name_to_id_{time_stamp}.json', subfolder=['training_data', 'fetched_data', dataset_name,'util_data'], allow_not_existing=True),name_to_id),
            (data_util.get_data_path(f'synergies_{time_stamp}.json', subfolder=['training_data', 'fetched_data', dataset_name,'fetched_data'], allow_not_existing=True),synergies),
            (data_util.get_data_path(f'binary_{time_stamp}.json', subfolder=['training_data', 'fetched_data', dataset_name,'fetched_data'], allow_not_existing=True),binary_data),
            (data_util.get_data_path(f'total_decks_{time_stamp}.json', subfolder=['training_data', 'fetched_data', dataset_name,'fetched_data'], allow_not_existing=True), total_decks),
        ]
        for datapath, variable in filepaths:
            json.dump(variable, open(datapath, 'w'), indent=4)
def convert_names_to_ids(name_to_id, ids_to_get, double_sided_id, lock):
    double_sided_id = [f'\'%{card}%\'' for card in double_sided_id]
    # Prepare parameter placeholders
    placeholders_ids = ', '.join(['?'] * len(ids_to_get))
    placeholders_double = ', '.join(['?'] * len(double_sided_id))

    # Full query using correct SQL syntax
    query = f'''
            SELECT oracle_id_front, name FROM cards
            WHERE name IN ({placeholders_ids})
               OR (name LIKE '% // %' AND name IN ({placeholders_double}))
            GROUP BY name
            '''

    # Combine parameters for both IN clauses
    params = tuple(ids_to_get) + tuple(double_sided_id)

    # Call your query
    all_cards = sql_card_operations.get_all_cards_by_query(query, params)
    lock.acquire()
    for id, card in all_cards:
        for side_name in card.split(' // '):
            name_to_id[side_name] = id
    lock.release()
    return [id for id, card in all_cards]

def add_synergy_to_var(combo, binary_data, synergies, total_decks, lock, price_category,cedh, color_identity, tribe, tags, salt):
    all_characteristics = [tags, tribe, price_category, color_identity]
    # total decks
    lock.acquire()
    for oracle_id in combo:
        if oracle_id not in total_decks:
            total_decks[oracle_id] = {}
            if color_identity not in total_decks[oracle_id]:
                total_decks[oracle_id][color_identity] = 0
                total_decks[oracle_id][color_identity] += 1

    # Binary
    key = '#'.join(combo)
    if key not in synergies:
        synergies[key] = 0
    synergies[key] += 1


    input = [combo, all_characteristics]
    output = (cedh, salt)
    combo_dict = [input, output] # card
    binary_data.append(combo_dict)
    lock.release()



