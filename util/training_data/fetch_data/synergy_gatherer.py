import config
from util.data_util import data_util, json_util, dir_util
import os
from util.training_data.fetch_data import fetch_deck_hashes, gather_deck_data, create_raw_dataset
import config

def get_synergies(threads=200, save_interval=10000, fetched_data_name='testing', number_of_decks=None, dummy_data=0.3):
    # setup folders
    root_folder_path = os.path.join(config.data_folder_path,'training_data','raw_datasets')
    general_data_folder_structure =     {
                                            'decklist_hashes.json':'[]',
                                            'name_data.json':'{}',
                                            'deck_characteristics.json':{"tags":[], "tribes":[]}
                                        }
    raw_dataset_folder_structure =      {
                                            'final_datasets':{
                                                'binary.json':[],
                                                'synergies.json':{},
                                                'adjusted_binary.json':[]
                                            },
                                            'fetched_data':{
                                                'total_decks.json':{},
                                                'synergies.json':{},
                                                'binary_data.json':[],
                                                'backups':{}
                                            },
                                            'raw_datasets':{
                                                'total_decks.json': {},
                                                'synergies.json': {},
                                                'binary_data.json': [],
                                                'backups': {}
                                            }
                                        }
    general_data_folder_path = os.path.join(root_folder_path, 'general_data')
    dir_util.create_folder_structure(general_data_folder_path, general_data_folder_structure)
    dataset_path = os.path.join(root_folder_path, fetched_data_name)
    if not os.path.exists(dataset_path):
        os.makedirs(dataset_path)
    dir_util.create_folder_structure(dataset_path, raw_dataset_folder_structure, overwrite=True)

    # get all decklist hashes
    all_hashes = json_util.get_data('decklist_hashes.json', subfolder=['training_data', 'raw_datasets', 'general_data'])
    if len(all_hashes)<1000:
        all_hashes = fetch_deck_hashes.get_all_hashes(threads)
    json_util.dump_data('decklist_hashes.json', all_hashes, subfolder=['training_data', 'raw_datasets', 'general_data'])

    # start_importing_decks
    binary_data, synergies, total_decks, name_data, deck_characteristics = gather_deck_data.add_all_decks(threads, save_interval, fetched_data_name, number_of_decks)

    # saving files
    list_of_files = [
                     (os.path.join(general_data_folder_path, 'deck_characteristics.json'), deck_characteristics),
                     (os.path.join(general_data_folder_path, 'name_data.json'), name_data),
                     (os.path.join(dataset_path,'fetched_data', 'total_decks.json'), total_decks),
                     (os.path.join(dataset_path,'fetched_data', 'synergies.json'), synergies),
                     (os.path.join(dataset_path,'fetched_data', 'binary_list.json'), binary_data),
        ]
    for file_name, data in list_of_files:
        #json_util.dump_data(file_name, data, subfolder=['training_data', fetched_data_name, 'final_fetched_data'])
        pass


    # create raw datasets
    create_raw_dataset.create_raw_dataset(binary_data, synergies, total_decks, dataset_path, dummy_data, name_data, deck_characteristics)
