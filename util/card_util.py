import json

from rapidfuzz.fuzz_py import ratio
from util import json_util
from util import data_util
import os


def get_card_index(search_dict, get_cheapest=True):
    index_map = json_util.get_data('database_index_map.json')
    if 'name' not in search_dict and 'id' not in search_dict:
        print('invalid query')
        return False
    if 'id' in search_dict:
        if search_dict['id'] in index_map:
            return index_map[search_dict['id']]['index']
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
                current_ratio = 0
                current_value = 0
                for key, value in current_dict.items():
                    key_ratio = ratio(key, search_dict[step])
                    if key_ratio > current_ratio:
                        current_ratio = key_ratio
                        current_value = value
                current_dict = current_value
        else:
            return current_dict['lowest']['index']


def get_dict_object_from_database(file, offset):
    if offset == 0:
        file.seek(0)
    else:
        char = ''
        while offset > 0:
            file.seek(offset - 1)
            char = file.read(1)
            if char == '\n':
                break
            offset -= 1
        file.seek(offset)

    line = file.readline()
    line = line.strip()[:line.rindex('}')+1]
    dict = json.loads(line)
    return dict

# either next target or av ob len

def get_card_dict(index, file=None, min=None, max=None, target=None):
    if not file:
        # define variables
        file_path = data_util.get_data_path('formatted_card_database.json')
        file = open(file_path, 'r', encoding='utf-8')
        file_length = os.path.getsize(file_path)
        min = 0
        max = file_length
        target = (min+max)/2
    # get dict
    dict = get_dict_object_from_database(file, target)
    dict_index = dict['index']

    # determine obj length
    if not average_obj_length:
        average_obj_length = file_length/(2*dict_index)
    # return or call
    if dict_index == index:
        return dict
    elif dict_index > index:
        average_object_length = (target-min)/
        next_target = 0
        return get_card_dict(index, file=file, min=min, max=target, target=)



