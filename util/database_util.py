from util import data_util
from util import json_util
from collections import defaultdict
import ijson
import simplejson
import json
import shutil
import time
# basics
def default_dict_tree():
    return defaultdict(default_dict_tree)



def update_index_map():
    index_map = default_dict_tree()

    with open(data_util.get_data_path("card_database.json", subfolder='database'), "r+", encoding="utf-8") as f:
        # first line
        formatted_file = open(data_util.get_data_path("formatted_card_database.json", subfolder='database'), "a", encoding="utf-8")
        formatted_file.write("[\n".replace("\'", "\""))
        parser = ijson.items(f, "item")
        for index, object in enumerate(parser):
            # add line to formatted database
            object["index"] = index
            formatted_file = open(data_util.get_data_path("formatted_card_database.json",subfolder='database'), "a", encoding="utf-8")
            object_string = simplejson.dumps(object, use_decimal=True)
            formatted_file.write(f"{object_string},\n")
            # get card variables
            price = object["prices"]["eur"]
            name_key = object["name"].lower()
            set_key = object["set"].lower()
            id = object['id']
            if isinstance(price, str):
                price = float(price)
            collector_number = object["collector_number"].lower()
            index_dict = {"price":price, "index": index}

            # write in index map
            index_map[name_key][set_key][collector_number] = index_dict
            index_map[id] = index_dict
            # set cheapest
            current_dict = index_map
            steps = [name_key, set_key]
            for step in steps:
                current_dict = current_dict[step]
                if isinstance(price, float) and ("lowest" not in current_dict or current_dict["lowest"]["price"]>price):
                    current_dict["lowest"] = index_dict
        # last line
        formatted_file = open(data_util.get_data_path("formatted_card_database.json",subfolder='database'), "a", encoding="utf-8")
        formatted_file.write("]".replace("\'", "\""))
        print("remove comma")

    json_util.dump_data("database_index_map.json", index_map)

def update_database():
    with open(data_util.get_data_path("formatted_card_database.json", subfolder='database'), "r+", encoding="utf-8") as f:
        lines = f.readlines()
        new_file = open(data_util.get_data_path("temp_database.json", subfolder='database'), "a", encoding="utf-8")
        updated_values_dict = json_util.get_data("card_values_to_update.json", subfolder='database')['cards']
        for line in lines:
            if '{' not in line:
                new_file.write(line)
            else:
                formatted_line = line.strip()[:line.rindex('}') + 1]
                dict = json.loads(formatted_line)
                if str(dict['index']) in updated_values_dict:
                    new_file.write(str(updated_values_dict[str(dict['index'])])+',\n')
                else:
                    new_file.write(line)
    shutil.move(data_util.get_data_path('temp_database.json', subfolder='database'), data_util.get_data_path('temp_database.json', subfolder='database'))
    json_util.dump_data('card_values_to_update.json', subfolder='database', data='{}')
update_database()