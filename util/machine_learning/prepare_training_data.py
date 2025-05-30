from util.json_util import dump_data, get_data
from random import randint

def data_preparation_1():
    data = get_data('full_import.json', ['machine_learning', 'training_data'])
    item = 0
    total = len(data['card_data'])
    # card synergies
    card_synergy_data = data['card_data']
    card_synergies = get_data('training_card_synergies_1.json', ['machine_learning', 'synergy_id_list'])
    for anchor_card, anchor_data in card_synergy_data.items():
        item +=1
        print(f'{item/total*100:.2f}%')
        # no tags
        total_anchor_decks = anchor_data['total']
        for card, second_data in anchor_data['pairing'].items():
            key = [card, anchor_card]
            key.sort()
            key = '+'.join(key)
            if key not in card_synergies:
                sub_synergy = second_data['total']/(total_anchor_decks['total'])
                card_synergies[key] = sub_synergy
        if item%1000==0:
            print('dumping')
            dump_data('training_card_synergies_1.json', card_synergies, ['machine_learning', 'synergy_id_list'])
    # no synergy card adding





data_preparation_1()