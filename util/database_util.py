from util import data_util
from util import json_util
from collections import defaultdict
import ijson
# basics
def default_dict_tree():
    return defaultdict(default_dict_tree)



def update_index_map():
    index_map = default_dict_tree()


    with open(data_util.get_data_path("card_database.json"), "r+", encoding="utf-8") as f:
        # first line
        formatted_file = open(data_util.get_data_path("formatted_card_database.json"), "a", encoding="utf-8")
        formatted_file.write("[\n".replace("\'", "\""))
        parser = ijson.items(f, "item")
        for index, object in enumerate(parser):
            # add line to formatted database
            object["index"] = index
            formatted_file = open(data_util.get_data_path("formatted_card_database.json"), "a", encoding="utf-8")
            formatted_file.write(f"{str(object)},\n".replace("\'", "\""))
            # get card variables
            price = object["prices"]["eur"]
            name_key = object["name"].lower()
            set_key = object["set"].lower()
            if isinstance(price, str):
                price = float(price)
            collector_number = object["collector_number"].lower()
            index_dict = {"price":price, "index": index}

            # write in index map
            index_map[name_key][set_key][collector_number] = index_dict
            # set cheapest
            current_dict = index_map
            steps = [name_key, set_key]
            for step in steps:
                current_dict = current_dict[step]
                if isinstance(price, float) and ("lowest" not in current_dict or current_dict["lowest"]["price"]>price):
                    current_dict["lowest"] = index_dict
        # last line
        formatted_file = open(data_util.get_data_path("formatted_card_database.json"), "a", encoding="utf-8")
        formatted_file.write("]".replace("\'", "\""))
        print("remove comma")

    json_util.dump_data("database_index_map.json", index_map)
update_index_map()
