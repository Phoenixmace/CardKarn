from util.data_util.json_util import get_data, dump_data, get_shared_data, update_shared_data
from tqdm import tqdm
from models.Card import BaseCard
from util.treading_util import ThreadingHandler
from random import shuffle
def prepare_card_pairs(method, data_file_name='', weights={}, threads=200, name=None, data_length=None):
    if not name:
        name = method

    data = get_data(data_file_name, ['machine_learning', 'training_data'])

    # direct_card_data
    card_data = data['card_data']

    # prepare params
    current_data_progress = get_data(f'temporary_dataset_cards_{name}.json', ['machine_learning', f'model_{name}'])
    if 'params' in current_data_progress:
        keys = current_data_progress['keys']
        inputs = current_data_progress['inputs']
        params = current_data_progress['params'][len(keys):]
    else:
        keys = []
        inputs = []
        already_added_card_1 = []
        params = []

        for card_1, card_1_data in tqdm(card_data.items(), desc='Preparing synergy arguments: ', ascii="-#",bar_format='{desc:<28.28}{percentage:3.0f}%|{bar:100}{r_bar}'):
            already_added_card_1.append(card_1)
            total_card_1_decks = card_1_data['total']['total']

            for card_2, card_2_data in card_1_data['pairing'].items():
                if card_2 not in already_added_card_1:
                    total_card_2_usage = card_2_data['total']
                    synergy = total_card_2_usage/total_card_1_decks
                    params.append((card_1, card_2, synergy))
        shuffle(params)
        if data_length:
            params = params[:data_length]
        dump_data(f'temporary_dataset_cards_{name}.json', {'params':params, 'keys':keys, 'inputs':inputs}, ['machine_learning', f'model_{name}'])


    threading_handler = ThreadingHandler(threads)
    subfolder_to_save = ['machine_learning', f"model_{name}"]
    files = [(f'categories_{name}.json', {'params':params, 'keys':keys, 'inputs':inputs}), (f'temporary_dataset_cards_{name}.json', None)]
    frequency = threads*20
    instructions = [(filename, frequency, subfolder_to_save, data) for filename, data in files]
    threading_handler.start_process([tuple(param) +(keys, inputs, method, weights, name)for param in params], add_card_synergy, process_message=f'Converting cards to training data', saving_instructions=instructions)
    dump_data(f'dataset_cards_{name}.json', {'keys':keys, 'inputs':inputs}, ['machine_learning', f'model_{name}'])









def add_card_synergy(card_name_1, card_name_2,synergy,keys, inputs, method, weights, name):#
    card_1 = BaseCard({'name': card_name_1}, wait_for_salt_score=True)
    card_2 = BaseCard({'name': card_name_2}, wait_for_salt_score=True)
    card_1_array = card_1.get_np_array(method=method, load_existing=False, name=name, weights=weights)
    card_2_array = card_2.get_np_array(method=method,load_existing=False, name=name, weights=weights)
    if not card_1_array or not card_2_array or len(card_1_array) != len(card_2_array):
        return
    arrays = sorted([card_1_array, card_2_array])
    arrays = arrays[0] + arrays[1]
    if synergy and arrays:
        inputs.append(arrays)
        keys.append(synergy)
