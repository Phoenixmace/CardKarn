from util.data_util import json_util
from util.threading_util import ThreadingHandler
import requests
from itertools import combinations
from util.database import sql_card_operations
import threading

def add_all_decks(threads, save_interval, dataset_name):
    threading_handler = ThreadingHandler(threads)
    all_hashes = json_util.get_data('decklist_hashes.json', ['datasets', dataset_name])
    name_to_id = json_util.get_data('name_to_id.json', ['datasets', dataset_name])
    synergies = json_util.get_data('synergies.json', ['datasets', dataset_name])
    total_decks = json_util.get_data('total_decks.json', ['datasets', dataset_name])
    lock = threading.Lock()
    params = [(hash, name_to_id, synergies, total_decks, lock, index%save_interval==0, dataset_name) for index, hash in enumerate(all_hashes)]
    threading_handler.start_process(params, add_deck, process_message='Gathering decks')

def add_deck(hash, name_to_id, synergies,total_decks, lock, save_data, dataset_name):
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
    color_identity = ''.join(color_identity)
    color_identity.sort()


    cedh = data['cedh']

    # tags

    tags = data['tags'] + data['edhrec_tags']
    tribe = data['tribe']
    if data['theme']:
        tags.append(data['theme'])
    if tribe:
        tags.append(tribe)
    tags = list(set(tags))
    tags.sort()

    salt = data['salt']


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
    id_decklist = []
    for card in decklist:
        card_id = None
        if card in name_to_id:
            card_id = name_to_id[card]
        else:
            card_dict = sql_card_operations.get_card_dict({'name':card})
            if card_dict:
                lock.acquire()
                name_to_id[card] = card_dict['scryfall_id']
                lock.release()
        if isinstance(card_id, str):
            id_decklist.append(card_id)
            if card_id not in total_decks:
                total_decks[card_id] = {'total':0}



    for combo in combinations(id_decklist, 2):
        combo.sort()
