from logging import getLogger

from rapidfuzz.fuzz_py import ratio
from util import database_util
from util import json_util
from util.process_time_tracker import Time_tracker
import rapidfuzz
import ijson
from util import data_util
from models import Card

def get_lowest_dict_by_price(current_dict, current_lowest_dict={'price': 10000, 'index':-1}):
    current_lowest_dict = current_lowest_dict
    for value in current_dict.values():
        if not ('price' in value and 'index' in value):
            value = get_lowest_dict_by_price(value, current_lowest_dict=current_lowest_dict)
        if (value['price'] and float(value['price']) < current_lowest_dict['price']) or current_lowest_dict['index'] == -1:
            if not value['price']:
                value['price'] = 10000
            current_lowest_dict = value


    return current_lowest_dict

def get_indices(search_dicts, get_cheapest=True):
    index_map = json_util.get_data('database_index_map.json')
    indices = []
    for search_dict in search_dicts:
        time_tracker = Time_tracker('Search Dict loop')
        if 'id' in search_dict and search_dict['id'] in index_map:
            indices.append(index_map[search_dict['id']])
        # get by name
        elif 'name' in search_dict:
            attribute_order = ['name', 'set', 'collector_number']
            current_index_map = index_map
            for attribute in attribute_order:
                attribute_time = Time_tracker('Attribute Time')

                # get next subdict
                if attribute in search_dict:
                    attribute_value = search_dict[attribute]

                    # direct hit
                    if attribute_value.lower() in current_index_map:
                        current_index_map = current_index_map[attribute_value.lower()]
                        attribute_time.get_time_stamp('direct hit')
                    else:
                        current_ratio = 0
                        current_key = ''
                        current_value = {}
                    # fuzzy search
                        for key, value in current_index_map.items():
                            obj_ratio = ratio(str(attribute_value), str(key))
                            if obj_ratio > current_ratio:
                                current_ratio = obj_ratio
                                current_key = key
                                current_value = value
                        print(f'{attribute_value} -> {current_key} ({current_ratio})')
                        current_index_map = current_value
                        attribute_time.get_time_stamp('ratio search')


                else:
                    current_index_map = get_lowest_dict_by_price(current_index_map)
                    time_tracker.get_time_stamp('one card(id)')
                    break
            indices.append(current_index_map['index'])


        else:
            print(search_dict, ' invalid')

        return indices

def get_card_dicts(indices):
    dict_list = []
    parser_load = Time_tracker()
    objects = database_util.get_parsed_objects(break_index=max(indices))
    parser_load.get_time_stamp('Parser Load')
    for index, dict in enumerate(objects):
        if index in indices:
            dict_list.append(dict)
            if len(dict_list) == len(objects):
                return dict_list
    return dict_list

def get_cards(search_params):
    indices = get_indices(search_params)
    dicts = get_card_dicts(indices)
    return dicts
