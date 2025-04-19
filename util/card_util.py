from util import json_util
import rapidfuzz
import ijson
from util import data_util
from util.format_database import return_dict


def get_card_dicts(list_of_names):
    # get indices
    index_map = json_util.get_data('database_index_map.json')
    indices_to_search = []
    not_found = {}
    # direct hits
    for card_name in list_of_names:
        if card_name in index_map:
            indices_to_search.append(index_map[card_name])
        else:
            not_found[card_name] = {'current_index': 0, "current_ratio":0}
    # search fuzzy
    for card_name_index in index_map:
        for key in not_found:
            ratio = rapidfuzz.fuzz.ratio(card_name_index, key)
            if ratio > not_found[key]['current_ratio']:
                not_found[key]['current_ratio'] = ratio
                not_found[key]['current_index'] = index_map[card_name_index]
                not_found[key]['current_name'] = card_name_index

    for card_name in not_found:
        indices_to_search.append(not_found[card_name]['current_index'])
        print(card_name, not_found[card_name]['current_name'], not_found[card_name]['current_ratio'])
    del index_map
    del not_found

    return_list = []
    with open(data_util.get_data_path('card_database.json'), 'r', encoding='utf-8') as f:
        parser = ijson.items(f, 'item')
        for index, obj in enumerate(parser):
            if index in indices_to_search:
                return_list.append(obj)
    return return_list




