from util.data_util import data_util, json_util
import os
from util.training_data import fetch_deck_hashes
from util.training_data.parse_deck_data import gather_deck_data


def get_synergies(threads=200, save_interval=10000, dataset_name='testing'):
    # get all decklist hashes
    decklist_json_path = data_util.get_data_path('decklist_hashes.json', subfolder=['datasets', dataset_name])
    if os.path.exists(decklist_json_path):
        all_hashes = json_util.get_data('decklist_hashes.json', subfolder=['datasets', dataset_name])
    else:
        with open(decklist_json_path, 'w') as f:
            f.write('{}')
        all_hashes = fetch_deck_hashes.get_all_hashes(threads)
        json_util.dump_data('decklist_hashes.json', all_hashes, subfolder=['datasets', dataset_name])

    # setup folder
    list_of_files = ['name_to_id.json', 'total_decks.json', 'synergies.json']
    for file_name in list_of_files:
        file_path = data_util.get_data_path(file_name, subfolder=['datasets', dataset_name])
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write('{}')

    # start_importing_decks
    gather_deck_data.add_all_decks(threads, save_interval, dataset_name)