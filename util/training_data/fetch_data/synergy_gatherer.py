from util.data_util import data_util, json_util
import os
from util.training_data.fetch_data import fetch_deck_hashes, gather_deck_data, create_raw_dataset


def get_synergies(threads=200, save_interval=10000, fetched_data_name='testing', number_of_decks=None, dummy_data=3):
    # setup folder
    root_folder_path = data_util.get_data_path(fetched_data_name, subfolder=['training_data', 'fetched_data'])
    if not os.path.exists(root_folder_path):
        os.makedirs(root_folder_path)
    list_of_subfolders = ['fetched_data', 'raw_datasets', 'util_data']
    for subfolder in list_of_subfolders:
        folder_path = data_util.get_data_path(subfolder, subfolder=['training_data', 'fetched_data', fetched_data_name])
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)


    list_of_files = [('name_to_id.json', 'util_data'), ('total_decks.json', 'fetched_data'), ('synergies.json', 'fetched_data'), ('binary_list.json', 'fetched_data')]
    for file_name, subfolder in list_of_files:
        file_path = data_util.get_data_path(file_name, subfolder=['training_data', 'fetched_data', fetched_data_name,subfolder])
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                if file_name == 'binary_list.json':
                    f.write('[]')
                else:
                    f.write('{}')

    # get all decklist hashes
    decklist_json_path = data_util.get_data_path('decklist_hashes.json', subfolder=['training_data', 'fetched_data', fetched_data_name, 'util_data'])
    if not os.path.exists(decklist_json_path):
        with open(decklist_json_path, 'w') as f:
            f.write('{}')
        all_hashes = fetch_deck_hashes.get_all_hashes(threads)
        json_util.dump_data('decklist_hashes.json', all_hashes, subfolder=['training_data', 'fetched_data', fetched_data_name, 'util_data'])

    # start_importing_decks
    binary_data, synergies, total_decks = gather_deck_data.add_all_decks(threads, save_interval, fetched_data_name, number_of_decks)

    # create raw datasets
    raw_dataset_path = data_util.get_data_path('raw_datasets', subfolder=['training_data', 'fetched_data', fetched_data_name])
    create_raw_dataset.create_raw_dataset(binary_data, synergies, total_decks, raw_dataset_path, dummy_data)
