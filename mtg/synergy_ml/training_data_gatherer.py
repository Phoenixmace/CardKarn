import time

import requests
import os
import json
import scrython

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
def get_all_decks(commander_name):
    return_dict = {}
    if '//' in commander_name:
        url_end = commander_name.split('//')[0]  # idea for var name Luc
    else:
        url_end = commander_name
    replace_char_dict = {
        'ó': 'o',
        ' ': '-',
        '!': '',
        ',': '',
        '\'': '',
    }
    for char in replace_char_dict:
        url_end = url_end.replace(char, replace_char_dict[char])

    url = f'https://json.edhrec.com/pages/decks/{url_end}.json'.lower()
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for index, key in enumerate(data['table']):
            return_dict[data['table'][index]['urlhash']] = {'price': data['table'][index]['price'], 'tags':data['table'][index]['tags'], 'salt': data['table'][index]['salt']}
    return return_dict
def get_decklist(deck_hash):
    url = f'https://edhrec.com/api/deckpreview/{deck_hash}'
    response = requests.get(url)
    return_dict = {}
    if response.status_code == 200:
        deck_data = response.json()
        return_dict = {
            'decklist': deck_data['cards'],
            'commander': deck_data['commanders'][0],
            'second_commander': deck_data['commanders'][1],
            'tags': deck_data['tags'],
            'theme': deck_data['theme'],
            'price': deck_data['price'],
            'salt': deck_data['salt'],
            'tribe': deck_data['tribe'],
            'type_distribution': {
                'enchantment':deck_data['enchantment'],
                'instant':deck_data['instant'],
                'land':deck_data['land'],
                'planeswalker':deck_data['planeswalker'],
                'sorcery':deck_data['sorcery'],
                'creature':deck_data['creature'],
                'artifact':deck_data['artifact'],
            },
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

    if not 'deck_stats' in data:
        data['deck_stats'] = {}

    # add_all_decklists
    top_commanders = data['added_commander_decklists']
    while len(data['added_commander_decklists']) > 0:
        print(f'Importing all hashes: {round(100-len(data['added_commander_decklists']) / len(data['commander_list'])*100, 2)}%')
        url_hashes = get_all_decks(data['added_commander_decklists'][0])
        for url_hash in url_hashes:
            if url_hash not in data['deck_stats']:
                data['deck_stats'][url_hash] = {}
        data['added_commander_decklists'] = data['added_commander_decklists'][1:]
        check_if_process_should_end(data)

    for index, url_hash in enumerate(data['deck_stats']):
        print(f'Importing all hashes: {round((index / len(data['deck_stats'])*100), 2)}%')
        recieved_data = False
        while not recieved_data:
            try:
                time.sleep(0.5)
                deck_data = get_decklist(url_hash)
                recieved_data = True
            except:
                pass

        if len(deck_data) < 1:
            data['deck_stats'][url_hash] = deck_data
        check_if_process_should_end(data)
    print('all finished')

def check_if_process_should_end(data):
    if os.path.exists("stop.txt"):
        print("Loop interrupted by file trigger.")
        dump_training_data(data)
        quit()
gather_data()