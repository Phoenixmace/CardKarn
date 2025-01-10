import json
import os

def get_data(file_path = 'data'):
    with open(get_card_data_path(file_path), 'r') as f:
        data = json.load(f)
    return data
def dump_data(data, file_path = 'data'):
    with open(get_card_data_path(file_path), 'w') as f:
        json.dump(data, f, indent=4)

def get_card_data_path(file_name):
    file_path = os.getcwd()+'\\mtg\\' + file_name +'.json'
    file_path = file_path.replace('\\','/')
    return file_path


