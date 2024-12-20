import json
import os


def get_card_data_path():
    file_path = os.getcwd()+'\\mtg\\data.json'
    file_path = file_path.replace('\\','/')
    return file_path

def get_data():
    with open(get_card_data_path(), 'r') as f:
        data = json.load(f)
    return data
def dump_data(data):
    with open(get_card_data_path(), 'w') as f:
        json.dump(data, f, indent=4)