import time
import itertools
from operator import index
from collections import defaultdict
import requests
import os
import json
from random import shuffle


def clean_name(name):
    if '//' in name:
        url_end = name.split('//')[0]  # idea for var name Luc
    else:
        url_end = name
    replace_char_dict = {
        'ó': 'o',
        ' ': '-',
        '!': '',
        ',': '',
        '\'': '',
    }
    for char in replace_char_dict:
        url_end = url_end.replace(char, replace_char_dict[char])
    return url_end

def get_all_commanders():
    # get data from all pages
    page = 1
    continute = True
    commanders = []
    json_data = load_training_data()
    while continute:
        try:
            url = f"""https://api.scryfall.com/cards/search?q=%28game%3Apaper%29+legal%3Acommander+is%3Acommander&order=none&unique=none&dir=none&include_variations=false&include_extras=false&include_multilingual=false&page={page}"""
            response = requests.get(url)
            data = response.json()
            for commander in data['data']:
                check_if_process_should_end(json_data)
                commander_name = commander['name']
                if commander_name not in commanders:

                    commanders.append(commander_name)
            print(data['total_cards'])
            page += 1

        except:
            continute = False
    json_data['commander_list'] = commanders
    return commanders

def get_commander_stats(commander_name):
    return_dict = {'combos':[]}
    url_end = clean_name(commander_name)
    url = f'https://json.edhrec.com/pages/commanders/{url_end}.json'.lower()
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'panels' in data and  'combocounts' in data['panels'] :
            for combo in data['panels']['combocounts']:
                if 'value' in combo:
                    return_dict['combos'].append(combo['value'].split(' + '))
    return return_dict
def get_all_decks(commander_name):
    deckhashes_return_dict = {}
    url_end = clean_name(commander_name)

    url = f'https://json.edhrec.com/pages/decks/{url_end}.json'.lower()
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for index, key in enumerate(data['table']):
            deckhashes_return_dict[data['table'][index]['urlhash']] = {'price': data['table'][index]['price'], 'tags':data['table'][index]['tags'], 'salt': data['table'][index]['salt']}
    return deckhashes_return_dict
def get_decklist(deck_hash):
    url = f'https://edhrec.com/api/deckpreview/{deck_hash}'
    response = requests.get(url)
    return_dict = {}
    if response.status_code == 200:
        deck_data = response.json()
        price = deck_data['price']

        if price < 100:
            price = 1
        elif price < 250:
            price = 2
        elif price < 1000:
            price = 3
        else:
            price = 4
        if deck_data['cedh']:
            cedh = 1
        else:
            cedh = 0
        detail_list = [f'is_cedh_{cedh}',f'price_class_{price}']
        detail_list.extend(deck_data['edhrec_tags'])
        if deck_data['tribe']:
            detail_list.append(deck_data['tribe'])
        if deck_data['tags']:
            detail_list.extend(deck_data['tags'])
        detail_list = set(detail_list)
        detail_list = list(detail_list)
        # edit decklist
        decklist = []
        basics = ["Mountain", "Island", "Wastes", "Forest", "Island"]
        for card in deck_data['cards']:
            if "Snow-Covered" not in card and card not in basics:
                decklist.append(card)

        return_dict = {
            'deck_details' :detail_list,
            'decklist': decklist,
            'commanders': deck_data['commanders'],
            'edhrec_tags': deck_data['edhrec_tags'],
            'salt': deck_data['salt'],

        }
    return return_dict
def load_training_data():
    file_path = os.getcwd() + '/deck_training_data' + '.json'
    file_path = file_path.replace('\\', '/')
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data
def dump_training_data(data, file_path = 'data'):
    file_path = os.getcwd() + '/deck_training_data' + '.json'
    file_path = file_path.replace('\\', '/')
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def gather_data():
    loaded_data = load_training_data()
    data = defaultdict(lambda: defaultdict(int), loaded_data)
    print("Running...")

    if not 'commander_list' in data:
        data['commander_list'] = get_all_commanders()

    if not 'added_commander_decklists' in data:
        data['added_commander_decklists'] = data['commander_list']


    if not 'list_of_decks' in data:
        data['list_of_decks'] = []
    if not 'card_data' in data:
        data['card_data'] = {}
    if not 'commander_data' in data:
        data['commander_data'] = {}

    # add_all_decklists
    while len(data['added_commander_decklists']) > 0:
        print(f'Importing all hashes: {round(100-len(data['added_commander_decklists']) / len(data['commander_list'])*100, 2)}%')
        url_hashes = get_all_decks(data['added_commander_decklists'][0])
        data['list_of_decks'] = list(set(url_hashes) | set(data['list_of_decks']))

        data['added_commander_decklists'] = data['added_commander_decklists'][1:]
        check_if_process_should_end(data)

    # add decks

    # create index
    if 'current_deck_index' not in data:
        data['current_deck_index'] = -1
        shuffle(data['list_of_decks'])
    deck_index = data['current_deck_index']

    # iterating over list
    while deck_index+1 < len(data['list_of_decks']):
        deck_index += 1
        print(f'Importing all decks: {round((deck_index / len(data['list_of_decks']) * 100), 2)}%')
        start = time.time()
        # save all few iterations
        if deck_index%100 == 0:
            check_if_process_should_end(data, current_index=deck_index, just_fucking_dump_it=True)
        check_if_process_should_end(data, current_index=deck_index)

        # get the decklist
        request_start = time.time()
        deck_data = None
        counter = 0
        while not deck_data and counter < 5:
            try:
                deck_data = get_decklist(data['list_of_decks'][deck_index])
            except:
                time.sleep(0.5)
                counter += 1
                pass
        request_time = time.time()- request_start
        # add combos
        for commander in deck_data['commanders']:
            if commander not in data['commander_data'] and commander:
                commander_data = get_commander_stats(commander)
                if 'combo' in commander_data:
                    combos = commander_data['combos']
                    for combo in combos:
                        for piece in combo:
                            if piece not in data['cards']:
                                data['card_data'][piece] = {}
                            if 'combos' not in data['card_data'][piece]:
                                data['card_data'][piece]['combos'] = []
                            other_pieces = []
                            for other_piece in combo:
                                if other_pieces != piece:
                                    other_pieces.append(other_piece)
                            other_pieces = other_pieces.sort()
                            if other_pieces not in data['card_data'][piece]['combos']:
                                data['card_data'][piece]['combos'].append(other_pieces)

        # add deck details to commander
        for detail in deck_data['deck_details']:
            for commander in deck_data['commanders']:
                if commander:
                    data.setdefault('commander_data', {}).setdefault(commander, {}).setdefault(detail, 0)
                    data['commander_data'][commander][detail] += 1
        # add cards
        for card in deck_data['decklist']:
            for commander in deck_data['commanders']:
                if commander:
                    data.setdefault('commander_data', {}).setdefault(commander, {}).setdefault(card, {}).setdefault('total', 0)
                    data['commander_data'][commander][card]['total'] += 1
                    for attribute in deck_data['deck_details']:
                        data.setdefault('commander_data', {}).setdefault(commander, {}).setdefault(card, {}).setdefault(
                            attribute, 0)
                        data['commander_data'][commander][card][attribute] += 1



            # add to card
            for intercard in deck_data['decklist']:
                if intercard != card and intercard not in deck_data['commanders']:
                    data.setdefault('card_data', {}).setdefault(card, {}).setdefault('matched_cards', {}).setdefault(
                        intercard, 0)
                    data['card_data'][card]['matched_cards'][intercard] += 1

        one_iteration = time.time() - start
        print(end='')





    print('all finished')

def check_if_process_should_end(data, current_index = None, just_fucking_dump_it = False):
    if os.path.exists("stop.txt") or just_fucking_dump_it:
        print("Loop interrupted by file trigger.")
        if current_index:
            data['current_deck_index'] = current_index
        dump_training_data(data)
        if not just_fucking_dump_it:
            quit()
gather_data()
#get_decklist("JI1BQbAq9DB_1f8TlaPDLg")
#get_commander_stats('Niv-Mizzet, Parun')