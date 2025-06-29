import math
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

def evaluate_card_synergy(card, synergies, commander_synergies, price_penalty, budget_scaling_factor, decklist, card_weight):
    # get commander_synergy
    commander_synergy = commander_synergies.get(card.id, 0)

    # get all card_synergies
    synergy_score = []
    for deck_card in decklist:
        deck_card_id = deck_card.id
        key = tuple(sorted((deck_card.id, card.id)))
        deck_card_synergy = synergies.get(key, 0)
        synergy_score.append(deck_card_synergy)
    absolute_value = sum(synergy_score)/len(synergy_score)*card_weight
    if price_penalty == False:
        return absolute_value
    else:
        price_penalty = price_penalty ** budget_scaling_factor
        relative_value = absolute_value / price_penalty
        return relative_value





class Deckbuilder:
    def __init__(self, commander_name, budget, model_name, tag=None, tribe=None, card_weight=1, user_id='1'):
        self.commander_name = commander_name
        self.budget = budget
        self.card_weight = card_weight
        self.model_name = model_name
        self.tag = tag
        self.tribe = tribe
        self.commander_object = BaseCard({'name': commander_name})
        self.user_id = user_id
        if not self.commander_object:
            print('Commander not found')
            return

    def build_deck(self):
        model_path = os.path.join(config.data_folder_path, 'neural_network', 'models', f'{self.model_name}.keras')
        # load model
        if not os.path.exists(model_path):
            print('model not found')
            return
        model = load_model(model_path)
        np_array_name = '1'
        # get cards
        edhrec_card_objects = get_all_edhrec_cards(self.commander_object)
        collection_card = get_cards_from_database(self.commander_object, self.user_id)

        synergies = {}
        commander_synergies ={}
        commander_tokens = self.commander_object.get_np_array(name=np_array_name)
        for card in edhrec_card_objects:
            card_tokens = card.get_np_array(name=np_array_name)
            prediction = model.predict([card_tokens, commander_tokens])[0][0]
            commander_synergies[card.id] = prediction

        for card in collection_card:
            card_tokens = card.get_np_array(name=np_array_name)
            prediction = model.predict([card_tokens, commander_tokens])[0][0]
            commander_synergies[card.id] = prediction

        for card1 in edhrec_card_objects:
            for card2 in collection_card:
                key = tuple(sorted((card1.id, card2.id)))  # sorted so (a, b) == (b, a)
                if key not in synergies:
                    tokens1 = np.expand_dims(card1.get_np_array(name=np_array_name), axis=0)  # shape becomes (1, 50)
                    tokens2 = np.expand_dims(card2.get_np_array(name=np_array_name), axis=0)
                    prediction = model.predict([tokens1, tokens2])[0][0]
                    synergies[key] = prediction
        generated_deck = self.generate_deck(edhrec_card_objects, collection_card, synergies, commander_synergies)
    def generate_deck(self, edhrec_cards, collection_cards, synergies, commander_synergies,price_penalty_weight = 0.35):
        # get factors
        budget = self.budget
        if budget <= 0: # eliminate math error
            budget_scaling_factor = 1
        else:
            budget_scaling_factor = ((4-math.log10(budget))/4)




        commander = self.commander_object
        deck_list = []
        deck_cost = 0
        for i in range(65):
            highest_synergy = 0
            highest_synergy_card = None
            for card in edhrec_cards:
                if 'Land' in card.type_line:
                    continue
                prices = card.prices
                price = min(prices.values())
                price_penalty = price_penalty_weight * (math.log10(price) + 1)
                card_score = evaluate_card_synergy(card, synergies,commander_synergies, price_penalty, budget_scaling_factor, deck_list, self.card_weight)
                if card_score > highest_synergy and card.id not in deck_list:
                    highest_synergy = card_score
                    highest_synergy_card = card
            for card in collection_cards:
                if 'Land' in card.type_line:
                    continue
                card_score = evaluate_card_synergy(card, synergies,commander_synergies, False, budget_scaling_factor, deck_list, self.card_weight)
                if card_score > highest_synergy and card.id not in deck_list:
                    highest_synergy = card_score
                    highest_synergy_card = card
            print(f'added {highest_synergy_card.name} with score {highest_synergy}')
        for card in deck_list:
            print(card.name)

