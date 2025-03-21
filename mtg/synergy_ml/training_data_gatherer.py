import time
import itertools
from operator import index

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
        print(data)
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
        detail_list = [cedh, price, deck_data['theme']]

        deck_detail_names = ['tags', 'edhrec_tags', 'tribe']
        for detail_name in deck_detail_names:
            if deck_data[detail_name]:
                print(deck_data[detail_name])
                for detail in list(deck_data[detail_name]):
                    if detail and detail != None:
                        detail_list.append(detail.lower())
        # edit decklist
        decklist = []
        basics = ["Mountain", "Island", "Wastes", "Forest", "Island"]
        for card in deck_data['cards']:
            if "Snow-Covered" not in card and card not in basics:
                decklist.append(card)

        return_dict = {
            'deck_details' :detail_list,
            'decklist': decklist,
            'cedh': deck_data['cedh'],
            'commanders': deck_data['commanders'],
            'tags': deck_data['tags'],
            'edhrec_tags': deck_data['edhrec_tags'],
            'theme': deck_data['theme'],
            'price': deck_data['price'],
            'salt': deck_data['salt'],
            'tribe': deck_data['tribe'],

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
    data = load_training_data()
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
        start = time.time()
        url_hashes = get_all_decks(data['added_commander_decklists'][0])

        request_time = time.time() -start
        iteration_start = time.time()
        for url_hash in url_hashes:
            start_e = time.time()
            if url_hash not in data['list_of_decks']:
                data['list_of_decks'].append(url_hash)
            check_and_append_time = time.time() -start_e
        whole_iteration_time = time.time() - iteration_start
        data['added_commander_decklists'] = data['added_commander_decklists'][1:]
        check_if_process_should_end(data)

    # add decks
    # create index
    if 'current_deck_index' not in data:
        data['current_deck_index'] = -1
        data['list_of_decks'] = shuffle(data['list_of_decks'])
    deck_index = data['current_deck_index']

    # iterating over list
    while deck_index+1 < len(data['list_of_decks']):
        deck_index += 1
        print(f'Importing all decks: {round((deck_index / len(data['list_of_decks']) * 100), 2)}%')

        # get the decklist
        recieved_data = False
        while not recieved_data:
            try:
                deck_data = get_decklist(data['list_of_decks'][deck_index])
                recieved_data = True
            except:
                time.sleep(0.5)
                pass

        # add combos
        for combo in get_commander_stats(data['list_of_decks'][deck_index])['combos']:
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

        # add cards
        added_general_commander_detail = False
        for card in deck_data['decklist']:
            if card not in data['card_data']:
                data['card_data'][card] = {}

            # add to commander
            for commander in deck_data['commanders']:
                if commander:

                    # create commander
                    if commander not in data['commander_data']:
                        data['commander_data'][commander] = {}
                    #create and save card total
                    if card not in data['commander_data'][commander]:
                        data['commander_data'][commander][card] = {'total':0}
                    data['commander_data'][commander][card]['total'] +=1
                    # save card details
                    for detail in deck_data['deck_details']:

                        if not added_general_commander_detail:
                            if detail not in data['commander_data'][commander]:
                                data['commander_data'][commander][detail] = 0
                            data['commander_data'][commander][detail] += 1
                            added_general_commander_detail = True

                        if detail not in data['commander_data'][commander][card]:
                            data['commander_data'][commander][card][detail] = 0
                        data['commander_data'][commander][card][detail] +=1

            # add to card
            for intercard in deck_data['decklist']:
                if intercard != card:
                    if intercard not in data['card_data'][card]:
                        data['card_data'][card]['matched_cards'][intercard] = 0
                    data['card_data'][card]['matched_cards'][intercard] += 1







    print('all finished')

def check_if_process_should_end(data, current_index = None):
    if os.path.exists("stop.txt"):
        print("Loop interrupted by file trigger.")
        if current_index:
            data['current_deck_index'] = current_index
        dump_training_data(data)
        quit()
gather_data()
get_decklist("JI1BQbAq9DB_1f8TlaPDLg")
get_commander_stats('Niv-Mizzet, Parun')