import json
import os
import config


def get_source_folder_path():
    source_folder_name = 'CardKarn'
    file_path = os.getcwd()
    folder_path = file_path[:file_path.index(source_folder_name)+len(source_folder_name)] + os.sep
    return folder_path
def get_data_path(filename, subfolder=[], allow_not_existing=True):
    # legacy reasons
    if isinstance(subfolder, str):
        subfolder = [subfolder]

    if config.data_folder_path:
        data_path = config.data_folder_path + os.sep
    else:
        data_path = get_source_folder_path() + 'data'
    for folder in subfolder:
        data_path = data_path + os.sep + folder
    filepath = data_path + os.sep + filename
    if os.path.exists(filepath) or allow_not_existing:
        return filepath
    else:
        print('filepath could not be found: ', filepath)
        return False
