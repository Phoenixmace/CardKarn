from util.data_util import json_util
from models.Card import BaseCard
import random
from util.treading_util import ThreadingHandler
from util.machine_learning import card_array
from util.data_util import json_util


def create_training_arrays(filename, method=1, filename_to_save='dataset.json'):
    data = json_util.get_data(filename_to_save, ['machine_learning', 'final_training_data'])

    if 'input' in data:
        input = data['input']
        key = data['key']
        shuffled_data = data['shuffled_data']
        absolute_index = data['index']
    else:
        data = json_util.get_data(filename, ['machine_learning', 'synergy_id_list'])
        shuffled_data = data['cards'].copy()
        random.shuffle(shuffled_data)
        input = []
        key = []
        absolute_index = 0
        data = {'key':key, 'input':input, 'index': absolute_index, 'shuffled_data':shuffled_data}
        #json_util.dump_data(filename_to_save, data, ['machine_learning', 'final_training_data'])


    threading_handler = ThreadingHandler(200)
    save_interval = 1000
    all_params = [(param, key, input, method, ((index+1)%save_interval==0, filename_to_save,data if (index+1)%save_interval==0 else None, threading_handler)) for index, param in enumerate(shuffled_data[absolute_index:])]
    threading_handler.start_process(all_params[:1001], add_synergy, process_message=f'Creating training arrays: ')

    shared_data = json_util.shared_json_data
    categories = shared_data['categories_1.json']
    json_util.dump_data('categories_1.json', categories, ['machine_learning', 'categorising_data'])
    json_util.dump_data(filename_to_save, data, ['machine_learning', 'final_training_data'])

def add_synergy(synergy, key, input, method, save_data):
    card_1 = BaseCard({'scryfall_id': synergy[0]}, wait_for_salt_score=True)
    card_2 = BaseCard({'scryfall_id': synergy[1]}, wait_for_salt_score=True)
    card_array_1 = card_1.get_np_array(method=method)
    card_array_2 = card_2.get_np_array(method=method)
    if not card_array_1 or not card_array_2 or len(card_array_1) != len(card_array_2):
        return

    key.append(synergy[2])
    arrays = sorted([card_array_1, card_array_2])
    arrays = arrays[0] + arrays[1]
    input.append(arrays)
    if len(input) != len(key):
        pass
        print(synergy, 'why is it not the same length?')
        quit()
    if save_data[0]:
        threading_handler = save_data[3]
        print('saving data...')
        for thread in threading_handler.threads:
            thread.join()
        json_util.dump_data(save_data[1], save_data[2], ['machine_learning', 'final_training_data'])



