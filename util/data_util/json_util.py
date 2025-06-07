import json
import util.data_util.data_util as data_util
import threading
treading_file_lock = threading.Lock()
def get_data(filename, subfolder=False, file_lock=False):
    filepath = data_util.get_data_path(filename, subfolder)
    if filepath:
        if file_lock:
            with treading_file_lock:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    return data
        else:
            with open(filepath, 'r') as f:
                data = json.load(f)
                return data
    else:
        return False


def dump_data(filename, data, subfolder=False, file_lock=None):
    filepath = data_util.get_data_path(filename, subfolder)
    if filepath:
        # file_lock
        if file_lock:
            with treading_file_lock:
                with open(filepath, 'w') as f:
                    if isinstance(data, (list, dict)):
                        json.dump(obj=data, fp=f, indent=4)
                        return True
                    else:
                        return False
        else:
            with open(filepath, 'w') as f:
                if isinstance(data,(list, dict)):
                    json.dump(obj=data, fp=f, indent=4)
                    return True
                else:
                    return False
    return filepath

def set_value(filename, dict_path: list, value, subfolder=None, create_path = True):
    data = get_data(filename=filename, subfolder=subfolder)
    current = data

    for key in dict_path[:-1]:
        if key in current:
            current = current[key]
        elif create_path:
            current[key] = {}
            current = current[key]
        else:
            print(dict_path, ' was not found in: ', filename)
            return False

    current[dict_path[-1]] = value
    dump_data(filename=filename, data=data, subfolder=subfolder)
    return True

def increment_value_by(filename, dict_path:list, increment_value=1, default_value=0, subfolder=None, create_path = True):
    data = get_data(filename=filename, subfolder=subfolder)
    current = data

    for key in dict_path[:-1]:
        if key in current:
            current = current[key]
        elif create_path:
            current[key] = {}
            current = current[key]
        else:
            print(dict_path, ' was not found in: ', filename)
            return False

    if dict_path[-1] in current:
        if isinstance(current[dict_path[-1]], (int, float)):
            current[dict_path[-1]] += increment_value
        else:
            print(f'cannot increase value of {type(current[dict_path[-1]])}')
    else:
        current[dict_path[-1]] = default_value + increment_value
    return dump_data(filename=filename, data=data, subfolder=subfolder)


