import math
import os
import sqlite3

from tqdm import tqdm
from itertools import combinations

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
    if len(color_idendity) < 5:
        color_query_section = [item for key, item in colors_dict.items() if key not in color_idendity]
        color_query_section = ' AND NOT '.join(color_query_section)
        color_query_section = f' AND NOT {color_query_section}'
    else:
        color_query_section = ''
    query = f'''SELECT json FROM cards WHERE commander_legal and scryfall_id = ? {color_query_section} LIMIT 1'''
    print(query)
    conn, cursor = get_cursor('cards.db')
    json_dicts = []
    for id in params:
        cursor.execute(query, (id))
        result = cursor.fetchone()
        if result:
            json_dicts.append(result[0])
    all_card_objects = [BaseCard(card_json=json.loads(json_dict)) for json_dict in json_dicts]
    all_cards = [card for card in all_card_objects if card.is_valid and card is not None and card.legalities['commander'] == 'legal']

    return all_cards

def clean_name(name):
    if '//' in name:
        url_end = name.split(' // ')[0]  # idea for var name Luc
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
        for list in json_dict['cardlists'][1:]:
            for card in list['cardviews']:
                cards.append(card['name'])
        return cards
    base_cards = get_cards(url)

    expensive_cards = get_cards(expensive_url)
    all_cards = list(set(base_cards + expensive_cards))
    all_cards = [BaseCard({'name': card}) for card in all_cards]
    all_cards = [card for card in all_cards if card.is_valid and card is not None]
    return all_cards

def evaluate_card_synergy(card, synergies, commander_synergies, price_penalty, budget_scaling_factor, decklist, card_weight):
    # get commander_synergy
    commander_synergy = commander_synergies.get(card.id, 0)
    # get all card_synergies
    synergy_score = []
    for deck_card in decklist:
        key = tuple(sorted((deck_card.id, card.id)))

        deck_card_synergy = synergies.get(key, 0)
        if deck_card_synergy == 0:
            print('no synergy found for ', key)
        synergy_score.append(deck_card_synergy)
    if len(synergy_score) == 0:
        synergy_score.append(0)

    synergy_score.append(commander_synergy)
    synergy_score = sorted(synergy_score, reverse=True)
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
        # remove duplicates
        unique_cards = []
        seen_names = set()

        for card in collection_card:
            if card.name not in seen_names:
                unique_cards.append(card)
                seen_names.add(card.name)
        collection_card = unique_cards


        synergies = {}
        commander_synergies ={}

        all_cards = edhrec_card_objects + collection_card

        oracle_inputs = []
        card_inputs = []

        # get commander synergies
        for card in all_cards:
            oracle_arr, card_arr = card.get_np_array(name=np_array_name)  # shape (2, 25)
            oracle_inputs.append(oracle_arr)  # (25,)
            card_inputs.append(card_arr)  # (25,)
        # Convert to NumPy arrays with batch shape
        oracle_inputs = np.array(oracle_inputs)  # shape (N, 25)
        card_inputs = np.array(card_inputs)  # shape (N, 25)

        # Commander data is same for all, repeat N times
        commander_oracle, commander_card = self.commander_object.get_np_array(name=np_array_name)
        commander_oracle_inputs = np.repeat([commander_oracle], len(edhrec_card_objects + collection_card), axis=0)  # shape (N, 25)
        commander_card_inputs = np.repeat([commander_card], len(edhrec_card_objects + collection_card), axis=0)  # shape (N, 25)
        # Predict in one call
        predictions = model.predict([
            oracle_inputs,
            card_inputs,
            commander_oracle_inputs,
            commander_card_inputs
        ], batch_size=32)
        for card, pred in zip(all_cards, predictions):
            commander_synergies[card.id] = float(pred[0])  # or pred if it's just a scalar
        # get card synergies
        def generate_unique_card_pairs(cards, np_array_name):
            keys = set()
            oracle_1_inputs = []
            card_1_inputs = []
            oracle_2_inputs = []
            card_2_inputs = []

            for card1, card2 in tqdm(combinations(cards, 2), desc="Generating unique card pairs", total=len(cards) * (len(cards) - 1) / 2):
                key = tuple(sorted((card1.id, card2.id)))

                oracle_arr1, card_arr1 = card1.get_np_array(name=np_array_name)
                oracle_arr2, card_arr2 = card2.get_np_array(name=np_array_name)

                oracle_1_inputs.append(oracle_arr1)
                card_1_inputs.append(card_arr1)
                oracle_2_inputs.append(oracle_arr2)
                card_2_inputs.append(card_arr2)
                keys.add(key)

            return oracle_1_inputs, card_1_inputs, oracle_2_inputs, card_2_inputs, keys

        oracle_1_inputs, card_1_inputs, oracle_2_inputs, card_2_inputs, keys = generate_unique_card_pairs(all_cards, np_array_name)

        oracle_1_inputs = np.array(oracle_1_inputs)  # shape (N, 25)
        card_1_inputs = np.array(card_1_inputs)  # shape (N, 25)
        oracle_2_inputs = np.array(oracle_2_inputs)  # shape (N, 25)
        card_2_inputs = np.array(card_2_inputs)  # shape (N, 25)

        predictions = model.predict([
            oracle_1_inputs,
            card_1_inputs,
            oracle_2_inputs,
            card_2_inputs
        ], batch_size=32, verbose=1)

        for pred, key in zip(predictions, keys):
            synergies[key] = float(pred[0])
        generated_deck = self.generate_deck(edhrec_card_objects, collection_card, synergies, commander_synergies)
    def generate_deck(self, edhrec_cards, collection_cards, synergies, commander_synergies,price_penalty_weight = 0.35):
        # get factors
        budget = self.budget
        budget_category = 2
        if budget <= 0: # eliminate math error
            budget_scaling_factor = 1
        else:
            budget_scaling_factor = ((4-math.log10(budget_category))/4)

        deck_list = []
        deck_cost = 0
        for i in range(65):
            deck_list =[card for card in deck_list if card is not None]
            highest_synergy = 0
            highest_synergy_card = None
            highest_price = 0
            for card in edhrec_cards:
                prices = card.prices
                try:
                    price = min([value for key, value in prices.items() if value and key not in ['tix']])
                    price = float(price.replace('$', ''))
                    if price < 0:
                        #print(f'no price found for {card.name}')
                        price = 40
                except:
                    price = 40
                    #print(f'no price found for {card.name}')

                if (card.name in [decklist_card.name for decklist_card in deck_list if decklist_card is not None]) or not hasattr(card, 'type_line') or 'Land' in card.type_line or budget < price + deck_cost:
                    continue
                price_penalty = price_penalty_weight * (math.log10(price) + 1)
                if price_penalty < 0:
                    price_penalty = 0
                card_score = evaluate_card_synergy(card, synergies,commander_synergies, price_penalty, budget_scaling_factor, deck_list, self.card_weight)

                if card_score > highest_synergy:
                    highest_synergy = card_score
                    highest_synergy_card = card
                    highest_price = price
            for card in collection_cards:
                if (card.name in [decklist_card.name for decklist_card in deck_list if decklist_card is not None]) or not hasattr(card, 'type_line') or 'Land' in card.type_line:
                    continue
                card_score = evaluate_card_synergy(card, synergies,commander_synergies, False, budget_scaling_factor, deck_list, self.card_weight)
                if card_score > highest_synergy:
                    highest_synergy = card_score
                    highest_synergy_card = card
                    highest_price = 0
            try:
                if highest_synergy_card is None:
                    continue
                #print(f'added {highest_synergy_card.name} with score {highest_synergy}')
                deck_list.append(highest_synergy_card)
                deck_cost += highest_price

            except Exception as e:
                #print(highest_synergy_card)
                #print(e)
                pass

        print(f'''
Budget: {budget}
Deck Cost: {deck_cost}
Decklist:''')
        for card in deck_list:
            print(f'1 {card.name}')

