import math
import os
import sqlite3

from tqdm import tqdm
from itertools import combinations

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import numpy as np
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

def get_all_edhrec_cards(commander, no_budget = False):
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

        # type_distribution
        type_distribution = {
            'creature': data.get('creature', 0),
            'enchantment': data.get('enchantment', 0),
            'instant': data.get('instant', 0),
            'land': data.get('nonbasic', 0),
            'basic': data.get('basic', 0),
            'sorcery': data.get('sorcery', 0),
            'artifact': data.get('artifact', 0),
            'battle': data.get('battle', 0),
            'planeswalker': data.get('planeswalker', 0),

        }
        json_dict = data['container']['json_dict']
        if no_budget:
            lists =  json_dict['cardlists'][1:1]
        else:
            lists =  json_dict['cardlists'][1:]
        for list in lists:
            for card in list['cardviews']:
                cards.append(card['name'])
        return cards, type_distribution
    base_cards, type_distribution = get_cards(url)



    expensive_cards, unused_type_distribution = get_cards(expensive_url)
    all_cards = list(set(base_cards + expensive_cards))
    all_cards = [BaseCard({'name': card}) for card in tqdm(all_cards, desc='fetching edhrec card objects')]
    all_cards = [card for card in all_cards if card.is_valid and card is not None]
    return all_cards, type_distribution

def evaluate_card_synergy(card, synergies, commander_synergies, price_penalty, budget_scaling_factor, decklist, card_weight=0.3):
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
        from keras.models import load_model
        model = load_model(model_path)
        np_array_name = '1'
        # get cards
        if self.budget > 1:
            edhrec_card_objects, type_distribution = get_all_edhrec_cards(self.commander_object)
        else:
            edhrec_card_objects, type_distribution = get_all_edhrec_cards(self.commander_object, no_budget = True)
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
        synerg = []
        for card, pred in zip(all_cards, predictions):
            synerg.append([card, pred[0]])
            commander_synergies[card.id] = float(pred[0])
        synerg.sort(key=lambda x: x[1], reverse=True)
        for synergyief in synerg:
            print(synergyief[0].name, synergyief[1])
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
        deck_list, deck_cost, cards_to_buy, basics = self.generate_deck(edhrec_card_objects, collection_card, synergies, commander_synergies, type_distribution)
        self.print_deck(deck_list, deck_cost, cards_to_buy, basics)
        return deck_list, basics,

    def generate_deck(self, edhrec_cards, collection_cards, synergies, commander_synergies, type_distribution, price_penalty_weight = 0.35):
        # get factors
        budget = self.budget
        budget_category = 2
        if budget <= 0: # eliminate math error
            budget_scaling_factor = 1
        else:
            budget_scaling_factor = ((4-math.log10(budget_category))/4)

        deck_list = []
        deck_cost = 0
        cards_to_buy = []
        def add_card_type(type, exclude_basics, number, deck_cost, deck_list, cards_to_buy):
            for i in range(number):
                deck_list =[card for card in deck_list if card is not None]
                highest_synergy = 0
                highest_synergy_card = None
                highest_price = 0

                # iterate edhrec
                for card in edhrec_cards:
                    is_type_condition_met = hasattr(card, 'type_line') and ('basic' not in card.type_line.lower() or not exclude_basics) and type in card.type_line.lower()
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

                    if (card.name in [decklist_card.name for decklist_card in deck_list if decklist_card is not None]) or not is_type_condition_met or budget < price + deck_cost:
                        continue
                    price_penalty = price_penalty_weight * (math.log10(price) + 1)
                    if price_penalty < 0:
                        price_penalty = 0
                    card_score = evaluate_card_synergy(card, synergies,commander_synergies, price_penalty, budget_scaling_factor, deck_list, self.card_weight)

                    if card_score > highest_synergy:
                        highest_synergy = card_score
                        highest_synergy_card = card
                        highest_price = price

                # iterate collection
                for card in collection_cards:
                    is_type_condition_met = hasattr(card, 'type_line') and ('basic' not in card.type_line.lower() or not exclude_basics) and type in card.type_line.lower()
                    if (card.name in [decklist_card.name for decklist_card in deck_list if decklist_card is not None]) or not is_type_condition_met:
                        continue
                    card_score = evaluate_card_synergy(card, synergies,commander_synergies, False, budget_scaling_factor, deck_list, self.card_weight)
                    if card_score > highest_synergy:
                        highest_synergy = card_score
                        highest_synergy_card = card
                        highest_price = 0
                try:
                    if highest_synergy_card is None:
                        continue
                    #print(highest_synergy_card.name, owned_card, highest_synergy_card.id)
                    deck_list.append(highest_synergy_card)
                    check_owned = highest_synergy_card.name in [card.name for card in collection_cards]
                    owned_card = check_owned
                    if not owned_card:
                        deck_cost += highest_price
                        cards_to_buy.append([highest_synergy_card, highest_price])


                except Exception as e:
                    #print(highest_synergy_card)
                    #print(e)
                    pass
            return deck_list, deck_cost, cards_to_buy
        for type, number in type_distribution.items():
            #print(type, number)
            deck_list, deck_cost, cards_to_buy = add_card_type(type, type!='basic', number, deck_cost, deck_list, cards_to_buy)

        # add basics
        basic_number = 99-len(deck_list)
        basics = []

        each_type_to_add = int(basic_number/len(self.commander_object.color_identity))
        basics_dict = {
            'W': 'Plains',
            'U': 'Island',
            'B': 'Swamp',
            'R': 'Mountain',
            'G': 'Forest'
        }
        if len(self.commander_object.color_identity) == 1:
            basics.append([basics_dict.get(self.commander_object.color_identity[0], 'Plains'), basic_number])
        else:
            for color in self.commander_object.color_identity:
                basics.append([basics_dict.get(color, 'Plains'), each_type_to_add])
            # add final basics
            last_basics = basic_number%len(self.commander_object.color_identity)
            for i in range(last_basics):
                basics[i][1] += 1
        return deck_list, deck_cost, cards_to_buy, basics

    def print_deck(self, decklist, deck_cost, cards_to_buy, basics):
        print(f'''''')
        deck_string = f'''Deck Cost: {deck_cost}\nCommander: {self.commander_object.name}\nBudget: {self.budget}\n\nDecklist:\n'''
        owned_category = '[Owned{noPrice}] '
        deck_string += f'1 {self.commander_object.name}[Commander' + '{top}]\n'
        for basic, number in basics:
            deck_string += f'{number} {basic} {owned_category}\n'
        for card, price in cards_to_buy:
            deck_string += f'1 {card.name}' + '\n'
        for card in decklist:
            if card.name not in [card.name for card, _ in cards_to_buy]:
                deck_string += f'1 {card.name} {owned_category}' + '\n'
        print(deck_string)
        self.save_deck(deck_string)
    def save_deck(self, string):
        path = os.path.join(config.data_folder_path, 'Decks', f'{self.commander_name}_{self.model_name}.txt')
        with open(path, 'w') as f:
            f.write(string)