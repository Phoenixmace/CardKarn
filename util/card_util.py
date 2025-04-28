from rapidfuzz.fuzz_py import ratio
from util import json_util


def get_card_index(search_dict, get_cheapest=True):
    index_map = json_util.get_data('database_index_map.json')
    if 'name' not in search_dict and 'id' not in search_dict:
        print('invalid query')
        return False
    if 'id' in search_dict:
        if search_dict['id'] in index_map:
            return index_map['id']['index']
        else:
            print('invalid id')
            return False
    # get from name query
    steps = ['name', 'set', 'collector']
    current_dict = index_map
    for step in steps:
        if step in search_dict:
            if search_dict[step].lower() in current_dict:
                current_dict = current_dict[search_dict[step].lower()]
            else:
                for key in current_dict.keys():
                    if
