import json
from util import data_util
from util import json_util
from collections import defaultdict
# basics
def default_dict_tree():
    return defaultdict(default_dict_tree)



def update_index_map():
    index_map = default_dict_tree()
    file = open(data_util.get_data_path('source_card_database.json'), encoding='utf-8')
    lines = file.readlines()

    # iterate over lines
    for line_number, line in enumerate(lines):
        if len(line)>5 and '{' in line and '}' in line:
            line_string = str(line[line.find('{'):line.rfind('}')+1])
            line_dict = json.loads(line_string)
            price = line_dict['prices']['eur']
            name_key = line_dict['name'].lower()
            set_key = line_dict['set'].lower()
            if isinstance(price, str):
                price = float(price)
            collector_number = line_dict['collector_number']
            index_map[name_key][set_key][collector_number.lower()] = {'index':line_number+1,'price':price}
            # log cheapest versions
            cheapest_overall = index_map[name_key].get('cheapest_index')
            if isinstance(price, float) and (not cheapest_overall or cheapest_overall['price'] > price):
                index_map[name_key]['cheapest_index'] = {'index': line_number + 1, 'price': price}

            # Second level (cheapest in set)
            cheapest_in_set = index_map[name_key][set_key].get('cheapest_index')
            if isinstance(price, float) and (not cheapest_in_set or cheapest_in_set['price'] > price):
                index_map[name_key][set_key]['cheapest_index'] = {'index': line_number + 1, 'price': price}
            # save id
            index_map[line_dict['id']] = line_number+1
    json_util.dump_data('database_index_map.json', index_map)
update_index_map()