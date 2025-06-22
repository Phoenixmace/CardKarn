from util.data_util import json_util
import math
import os
import json
import random
from tqdm import tqdm


def create_raw_dataset(binary_data, raw_synergies, total_decks, save_path, dummy_data, name_data, deck_characteristics):
    synergies = get_synergies(raw_synergies, total_decks, name_data)
    direct_binary_data, adjusted_binary_data = get_binary_data(binary_data, raw_synergies, dummy_data, total_decks, deck_characteristics)

    print('Almost Done!!!')
    print('saving synergy data...')
    json.dump(synergies, open(os.path.join(save_path, 'final_datasets', 'synergies.json'), 'w'), indent=4)
    print('saving binary data...')
    json.dump(direct_binary_data, open(os.path.join(save_path, 'final_datasets', 'binary.json'), 'w'), indent=4)
    print('saving adjusted binary data...')
    json.dump(adjusted_binary_data, open(os.path.join(save_path, 'final_datasets', 'adjusted_binary.json'), 'w'), indent=4)


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
        must_include_colors = list(set(color_identity_1 + color_identity_2))

        # get all possible keys and add total decks
        posible_card_1_decks = 0
        posible_card_2_decks = 0
        for key, item in total_decks_1.items():
            if all([color in key for color in must_include_colors]):
                posible_card_1_decks += item
        for key, item in total_decks_2.items():
            if all([color in key for color in must_include_colors]):
                posible_card_2_decks += item
        synergy_value = get_synergy_score(posible_card_1_decks, posible_card_2_decks, value)
        # evaluate and add synergy
        if synergy_value and synergy:
            inputs.append([card_id_1, card_id_2])
            outputs.append(synergy_value)
    return {'inputs':inputs, 'outputs':outputs}

def get_synergy_score(card_1, card_2, decks_together):
    if card_2*card_1 == 0:
        #print('p_a*p_b = 0')
        return float('0.'+ str(random.randint(4,8)))
    else:
        #print('success')
        pass
    total_decks = card_1 + card_2
    p_a = card_1 / total_decks
    p_b = card_2 / total_decks

    p_ab = decks_together / total_decks
    if p_ab == 0:
        return float('-inf')
    return math.log2(p_ab / (p_a * p_b))
def get_binary_data(binary_data, synergies, dummy_data, total_decks, deck_characteristics):
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
    for i in tqdm(range(int(len(inputs)*dummy_data)), desc='Adding dummy data'):
        key = None
        while key == None or (key in synergies or key.split('#')[0] == key.split('#')[1]):
            random_id_1 = random.choice([key for key in total_decks.keys()])
            random_id_2 = random.choice([key for key in total_decks.keys()])
            key = [random_id_1, random_id_2]
            key.sort()
            key = '#'.join(key)
        # random color idendity
        random_color_identity = []
        for i in range(5):
            random_color_identity.append(random.choice(['B', 'U', 'G', 'R', 'W']))
        random_color_identity = set(random_color_identity)
        random_color_identity = list(random_color_identity)
        random_color_identity.sort()
        random_color_identity = ''.join(random_color_identity)

        # random tag
        random_tags = []
        for i in range(2):
            if random.randint(0, 2) == 2:
                random_tags.append(random.choice(deck_characteristics['tags']))

        # random tribe
        random_tribes = []
        for i in range(2):
            if random.randint(0, 20) == 2:
                random_tribes.append([random.choice(deck_characteristics['tribes'])])
        # get price category
        random_price = random.randint(1, 4)
        # get deck characteristics
        random_deck_characteristics = [random_tags, random_tribes, random_color_identity, random_price]
        # score
        score_multiplier = '0.'
        for i in range(2):
            score_multiplier += str(random.randint(0, 5))
        score_multiplier = round(float(score_multiplier), 2)

        score = score_multiplier * min_value
        key = [[random_id_1, random_id_2], random_deck_characteristics]

        # add data
        adjusted_inputs.append(key)
        adjusted_outputs.append(score)
        inputs.append(key)
        outputs.append(0)

    return {'inputs': inputs, 'outputs': outputs}, {'inputs': adjusted_inputs, 'outputs': adjusted_outputs}

def get_binary_score(output):
    cedh = output[0]
    salt = output[1]
    if not salt:
        salt = 1
    adjusted_salt = math.log(salt, 10)
    if cedh:
        return round(adjusted_salt * 1.3 -1, 2)
    else:
        return round(adjusted_salt -1, 2)