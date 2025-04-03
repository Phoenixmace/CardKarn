import json
import util.data_util as data_util

def get_data(filename, subfolder=False):
    filepath = data_util.get_data_path(filename, subfolder)
    if filepath:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return data
    else:
        return False

def dump_data(filename, data, subfolder=False):
    filepath = data_util.get_data_path(filename, subfolder)
    if filepath:
        with open(filepath, 'w') as f:
            json.dump(obj=data, fp=f)
            return True
    return filepath