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

def get_decklist_dict(deck_hash):
    url = f'https://edhrec.com/api/deckpreview/{deck_hash}'

    response_status = 5
    while response_status != 200 and response_status !=0:
        if 5 == response_status:
            time.sleep(0.1)
        response = requests.get(url)
        if response.status_code == 200:
            response_status = response.status_code
            deck_data = response.json()
        else:
            response_status -=1
    # return for not found page
    if response_status == 0:
        return False

    # make return_dict
    return_dict = {}


    price = deck_data['price']
    price_categories = {
        price < 1000: 3,
        price < 250: 2,
        price < 100: 1,

    } #price
    price_category = price_categories.get(True, 4)
    del price

    # cedh factor
    cedh = int(bool(deck_data['cedh'])) + 1

    # deck_details
    detail_list = ['total', f'price_class_{price_category}']
    detail_list.extend(deck_data['edhrec_tags'])
    if deck_data['tribe']:
        detail_list.append(deck_data['tribe'])
    if deck_data['tags']:
        detail_list.extend(deck_data['tags'])
    detail_list = list(set(detail_list))

    # Decklist
    basics = ["Mountain", "Island", "Wastes", "Forest", "Island"]
    decklist = [x for x in deck_data['cards'] if (x not in basics and 'Snow-Covered' not in x and x not in deck_data['commanders'])]

    # commanders
    commanders = deck_data['commanders']

    # return dict
    return_dict = {
        'commander_data':
            {commander:
                 {card:
                      {attribute:
                           cedh
                       for attribute in detail_list}
                  for card in decklist}
             for commander in commanders if commander},
        'card_data':
            {primary_card:
                 {'pairing':
                      {secondary_card:
                           {attribute:
                                cedh
                            for attribute in detail_list}
                       for secondary_card in decklist + commanders if secondary_card and (secondary_card != primary_card)}}
             for primary_card in decklist + (commanders) if primary_card}
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
    iteration_time_list = []
    while deck_index+1 < len(data['list_of_decks']):
        deck_index += 1
        start = time.time()

        # save all few iterations
        if deck_index%100 == 0:
            check_if_process_should_end(data, current_index=deck_index, just_fucking_dump_it=True)
        check_if_process_should_end(data, current_index=deck_index)

        deck_dict = get_decklist_dict(data['list_of_decks'][deck_index])
        increment_dict_by_1(data, deck_dict)
        del deck_dict

        iteration_time = time.time() -start
        iteration_time_list.append(iteration_time)
        iteration_time_list = iteration_time_list[:9]
        print(f'Importing all decks: {round((deck_index / len(data['list_of_decks']) * 100), 2)}% (estimated time: {round((sum(iteration_time_list)/len(iteration_time_list))*(len(data['list_of_decks']) - deck_index)/3600, 2)}h)')
        print(end='')





    print('all finished')

def check_if_process_should_end(data, current_index = None, just_fucking_dump_it = False):
    if os.path.exists("stop.txt") or just_fucking_dump_it:
        if current_index:
            data['current_deck_index'] = current_index
        dump_training_data(data)
        if not just_fucking_dump_it:
            print("Loop interrupted by file trigger.")
            quit()

def increment_dict_by_1(data, add_dict): # code from AI but understood and too lazy to copy
    stack = [(data, add_dict)]

    while stack:
        current_data, current_add = stack.pop()

        for key, value in current_add.items():
            if isinstance(value, dict):
                current_data[key] = current_data.get(key, {})
                stack.append((current_data[key], value))
            elif isinstance(value, int):
                current_data[key] = current_data.get(key, 0) + value
            elif isinstance(value, list):
                current_data.setdefault(key, [])
                if value not in current_data[key]:  # Avoid linear search if possible
                    current_data[key].append(value)

gather_data()
#get_decklist("JI1BQbAq9DB_1f8TlaPDLg")
#get_commander_stats('Niv-Mizzet, Parun')