from util import json_util
from models.Card import BaseCard
import random

def create_training_arrays(filename, method=1):
    data = json_util.get_data(filename, ['machine_learning', 'synergy_id_list'])
    data = data['cards']
    random.shuffle(data)
    input = []
    key = []
    for synergy in data:
        card_1 = BaseCard({'scryfall_id': synergy[0]}, wait_for_salt_score=True)
        card_2 =  BaseCard({'scryfall_id': synergy[1]}, wait_for_salt_score=True)
        card_array_1 = card_1.get_np_array(method=method)
        card_array_2 = card_2.get_np_array(method=method)
        key.append(synergy[2])
        arrays = sorted([card_array_1, card_array_2])
        arrays = arrays[0] + arrays[1]
        input.append(arrays)
