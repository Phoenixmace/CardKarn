from util.database import sql_card_operations
from itertools import combinations
import math
import os
import json
import random
from tqdm import tqdm


def create_raw_dataset(binary_data, synergies, total_decks, save_path, dummy_data):
    save_path = save_path + os.sep
    synergies = get_synergies(synergies, total_decks)
    json.dump(synergies, open(save_path+'synergies.json', 'w'), indent=4)

    # binary
    dummy_data = int(dummy_data)
    direct_binary_data, adjusted_binary_data = get_binary_data(binary_data, synergies, dummy_data)


def get_synergies(synergies, total_decks):
    id_to_color_identity = {}
    inputs = []
    outputs = []
    for synergy, value in tqdm(synergies.items(), desc='Converting synergies:'):
        split_synergy = synergy.split("#")
        card_id_1 = split_synergy[0]
        card_id_2 = split_synergy[1]
        total_decks_1 = total_decks[card_id_1]
        total_decks_2 = total_decks[card_id_2]

        # get color idendity
        if card_id_1 not in id_to_color_identity or card_id_2 not in id_to_color_identity:
            query = '''
            SELECT oracle_id_front, black_in_color_identity, blue_in_color_identity, green_in_color_identity, red_in_color_identity, white_in_color_identity FROM cards
            where oracle_id_front = ? or oracle_id_front = ?'''
            params = (card_id_1, card_id_2)
            results = sql_card_operations.get_all_cards_by_query(query, params)
            filtered_results = []
            for result in results:
                result = result
                if result not in filtered_results:
                    filtered_results.append(result)
                if len(filtered_results) == 2:
                    break

                if len(filtered_results) == 2:
                    for filtered_result in filtered_results:
                        id_to_color_identity[filtered_result[0]] = filtered_result[1:]

        else:
            card_1_color_identity = [None]+id_to_color_identity[card_id_1]
            card_2_color_identity = [None]+id_to_color_identity[card_id_2]
            filtered_result = (card_1_color_identity, card_2_color_identity)
        colors = ['B', 'U', 'G', 'R', 'W']
        possible_included_colors = []
        posible_card_1_decks = 0
        posible_card_2_decks = 0
        if results and len(filtered_result) == 2:
            for i in range(5):
                if filtered_result[0][i+1] == 1 or filtered_result[1][i+1] == 1:
                    possible_included_colors.append(colors[i])

        # get all possible keys and add total decks
        for key, item in total_decks_1.items():
            if all(letter in key for letter in possible_included_colors):
                posible_card_1_decks += item
        for key, item in total_decks_2.items():
            if all(letter in key for letter in possible_included_colors):
                posible_card_2_decks += item
            synergy_value = get_synergy_score(posible_card_1_decks, posible_card_2_decks, value)
            if synergy_value and synergy:
                inputs.append([card_id_1, card_id_2])
                outputs.append(synergy_value)
    return {'inputs':inputs, 'outputs':outputs}
def get_synergy_score(card_1, card_2, decks_together):
    total_decks = card_1 + card_2
    p_a = card_1 / total_decks
    p_b = card_2 / total_decks
    p_ab = decks_together / total_decks
    if p_ab == 0:
        return float('-inf')
    return math.log2(p_ab / (p_a * p_b))
def get_binary_data(binary_data, synergies, dummy_data):
    random.shuffle(binary_data)
    inputs = []
    outputs = []
    adjusted_inputs = []
    adjusted_outputs = []
    for combo in tqdm(binary_data, desc='Converting binary data'):
        inputs.append(combo[0])
        outputs.append(1)
        adjusted_inputs.append(combo[0])
        synergy = get_binary_score(combo[1])
        adjusted_outputs.append(synergy)


    # dummy data
    min_value = min(adjusted_outputs)
    for i in tqdm(range(len(inputs)*dummy_data), desc='Adding dummy data'):
        list_of_keys = list(synergies.keys())
        key = None
        while key == None or key in inputs:
            random_index_1 = random.randint(0, len(list_of_keys)-1)
            random_index_2 = random.randint(0, len(list_of_keys)-1)
            random_id_1 = random_index_1.split('#')[0]
            random_id_2 = random_index_2.split('#')[1]
            key = [random_id_1, random_id_2]
            key.sort()
            key = '#'.join(key)
        random_color_identity = []
        for i in range(5):
            random_color_identity.append(random.choice(['B', 'U', 'G', 'R', 'W']))
        random_color_identity = set(random_color_identity)
        random_color_identity = list(random_color_identity)
        random_color_identity = ''.join(random_color_identity)

        score_multiplier = str(random.randint(0, 1))
        score_multiplier += '.'
        for i in range(2):
            score_multiplier += str(random.randint(0, 9))
        score_multiplier = float(score_multiplier)
        score = score_multiplier * min_value








    return {'inputs':inputs, 'outputs':outputs} , {'inputs':adjusted_inputs, 'outputs':adjusted_outputs}

def get_binary_score(output):
    cedh = output[0]
    salt = output[1]
    if not salt:
        salt = 1
    adjusted_salt = math.log(salt, 5)
    if cedh:
        return adjusted_salt * 1.3
    else:
        return adjusted_salt