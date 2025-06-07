from util.data_util import data_util, json_util
from util.data_util.json_util import get_data, dump_data
import os
from util.machine_learning import prepare_training_data
from util.machine_learning import training_model

def create_new_card_model(method, data_file_name, weights={}, threads=300, name=None, max_training_data_entries=None):
    if not name:
        name = method
    # creating_necessairy_files
    file_names = ['categories', 'dataset_cards', 'data_set_commander', 'temporary_dataset_cards']
    folder_name = f"model_{name}"
    # folder
    folder_path = data_util.get_data_path(folder_name, subfolder=['machine_learning'], allow_not_existing=True)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # files
    for file_name in file_names:
        file_path = data_util.get_data_path(f'{file_name}_{name}.json', subfolder=['machine_learning', folder_name], allow_not_existing=True)
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write('{}')

    # prepare training data for cards
    prepare_training_data.prepare_card_pairs(method, data_file_name, weights, threads, name=name, data_length=max_training_data_entries)
    # train model for cards
    training_model.train_card_model(name, method, 'generic_model')



