from util.data_util import json_util
import math
import os
import json
import random
from tqdm import tqdm


def create_raw_dataset(binary_data, synergies, total_decks, save_path, dummy_data, name_data):
    save_path = save_path + os.sep
    synergies = get_synergies(synergies, total_decks, name_data)
    json.dump(synergies, open(save_path+'synergies.json', 'w'), indent=4)

    # binary
    dummy_data = int(dummy_data)
    direct_binary_data, adjusted_binary_data = get_binary_data(binary_data, synergies, dummy_data)


def get_synergies(synergies, total_decks, name_data):
    inputs = []
    outputs = []
    for synergy, value in tqdm(synergies.items(), desc='Converting synergies'):
        split_synergy = synergy.split("#")
        card_id_1 = split_synergy[0]
        card_id_2 = split_synergy[1]
        total_decks_1 = total_decks[card_id_1]
        total_decks_2 = total_decks[card_id_2]

        # get color idendity
        if card_id_1 not in name_data or card_id_2 not in name_data:
            continue
        color_identity_1 = name_data[card_id_1]
        color_identity_2 = name_data[card_id_2]
        # get all possible color combinations
        must_include_colors = [color_identity_2[i] for i in range(5) if color_identity_2[i]==1 or color_identity_1[i]==1]

        # get all possible keys and add total decks
        posible_card_1_decks = 0
        posible_card_2_decks = 0
        for key, item in total_decks_1.items():
            if (len(key) >= must_include_colors and all(must_include_color in key for must_include_color in must_include_colors)) or (key=='C' and len(must_include_colors)==0):
                posible_card_1_decks += item
        for key, item in total_decks_2.items():
            if len(key) >= must_include_colors and all(must_include_color in key for must_include_color in must_include_colors) or (key=='C' and len(must_include_colors)==0):
                posible_card_2_decks += item
        synergy_value = get_synergy_score(posible_card_1_decks, posible_card_2_decks, value)
        # evaluate and add synergy
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
    deck_characteristics = json_util.get_data('deck_characteristics.json', ['training_data','general_data'])

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
        random_color_identity.sort()
        random_color_identity = ''.join(random_color_identity)

        random_tags = []
        for i in range(2):
            if random.randint(0, 2) == 2:
                random_tags.append(random.choice(deck_characteristics['tags']))
        random_tribe = None

        score_multiplier = random.choice(['0', '0', '0', '1'])
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