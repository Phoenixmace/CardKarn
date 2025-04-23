import ijson
from util import data_util
from util import json_util
from collections import defaultdict
# basics
def default_dict_tree():
    return defaultdict(default_dict_tree)


def get_parsed_objects(break_index = None):
    return_list = []
    with open(data_util.get_data_path('card_database.json'), 'r', encoding='utf-8') as f:
        parser = ijson.items(f, 'item')
        for index, object in enumerate(parser):
            return_list.append([index,object])
            if break_index and break_index < index:
                return return_list
    return return_list

def update_index_map():
    index_map = default_dict_tree()
    card_list = get_parsed_objects()
    for object in card_list:
        card_index = object[0]
        card_dict = object[1]
        price = card_dict['prices']['eur']
        if isinstance(price, str):
            price = float(price)
        collector_number = card_dict['collector_number']
        index_map[card_dict['name'].lower()][card_dict['set'].lower()][collector_number.lower()] = {'index':card_index,'price':price}
        index_map[card_dict['id']] = card_index

    json_util.dump_data('database_index_map.json', index_map)
