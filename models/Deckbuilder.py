import os
import sqlite3

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import numpy as np
from keras.models import load_model
import config
from models.Card import BaseCard
import requests
from util.database.sql_util import get_cursor
import json

def get_cards_from_database(commander, user_id='1'):
    db_path = os.path.join(config.data_folder_path, 'sql', 'user_tables', f'{user_id}.db')
    con = sqlite3.connect(db_path)
    cursor = con.cursor()
    query = '''select scryfall_id from collection'''
    cursor.execute(query)
    all_ids = cursor.fetchall()

    params = []
    for id in all_ids:
        params.append(id)

    color_idendity = commander.color_identity
    colors_dict = {
        'W': 'white_in_color_identity',
        'U': 'blue_in_color_identity',
        'B': 'black_in_color_identity',
        'R': 'red_in_color_identity',
        'G': 'green_in_color_identity'
    }
    if len(color_idendity) >0:
        color_query_section = [item for key, item in colors_dict.items() if key not in color_idendity]
        color_query_section = ' AND NOT '.join(color_query_section)
        color_query_section = f' NOT {color_query_section}'
    else:
        color_query_section = ''
    query = f'''SELECT json FROM cards WHERE commander_legal and scryfall_id = ? and {color_query_section} LIMIT 1'''
    conn, cursor = get_cursor('cards.db')
    json_dicts = []
    for id in params:
        cursor.execute(query, (id))
        result = cursor.fetchone()
        if result:
            json_dicts.append(result[0])
    all_card_objects = [BaseCard(card_json=json.loads(json_dict)) for json_dict in json_dicts]

    return all_card_objects







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

def get_all_edhrec_cards(commander):
    edhrec_name = clean_name(commander.name)
    url = f'https://json.edhrec.com/pages/commanders/{edhrec_name}'.lower()
    expensive_url = f'{url}/expensive.json'
    url = f'{url}.json'
    def get_cards(edhrec_url):
        cards = []
        response = requests.get(edhrec_url)
        if response.status_code == 200:
            data = response.json()
        else:
            print('Error getting Data: ', edhrec_url)
            return cards

        json_dict = data['container']['json_dict']
        for list in json_dict['cardlists']:
            for card in list['cardviews']:
                cards.append(card['name'])
        return cards
    base_cards = get_cards(url)
    expensive_cards = get_cards(expensive_url)
    all_cards = list(set(base_cards + expensive_cards))
    all_cards = [BaseCard({'name': card}) for card in all_cards]
    all_cards = [card for card in all_cards if card.is_valid]
    return all_cards




class Deckbuilder:
    def __init__(self, commander_name, budget, model_name, tag=None, tribe=None, card_weight=1, user_id='1'):
        self.commander_name = commander_name
        self.budget = budget
        self.model_name = model_name
        self.tag = tag
        self.tribe = tribe
        self.commander_object = BaseCard({'name': commander_name})
        self.user_id = user_id
        if not self.commander_object:
            print('Commander not found')
            return

    def build_deck(self):
        # load model
        edhrec_card_objects = get_all_edhrec_cards(self.commander_object)
        collection_card_ids = get_cards_from_database(self.commander_object, self.user_id)
        model_path = os.path.join(config.data_folder_path, 'neural_network', 'models', f'{self.model_name}.keras')
        if not os.path.exists(model_path):
            print('model not found')
            return
        model = load_model(model_path)





