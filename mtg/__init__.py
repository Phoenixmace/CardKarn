import json
import os

def get_card_data_path():
    file_path = os.getcwd()
    if 'mtg' in file_path:
        file_path = file_path + '\\data.json'
    else:
        file_path = file_path + '\\mtg\\data.json'
    file_path = file_path.replace('\\','/')
    return file_path

def create_data_strucure():
    with open(get_card_data_path(), 'r') as f:
        data = json.load(f)
        if data:
            pass
        else:
            data['bulk'] =dict()
            data['bulk']['main'] =dict()
            data['decks'] = dict()
            data['memory'] = dict()
            with open(get_card_data_path(), 'w') as f:
                json.dump(data, f, indent=4)
            create_data_strucure()
def create_necessairy_files():
    file_path = os.getcwd()
    if 'mtg' in file_path:
        file_path = file_path + '\\images'
    else:
        file_path = file_path + '\\mtg\\images'
    file_path = file_path.replace('\\', '/')
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_path = get_card_data_path()
    if not os.path.exists(file_path):
        with open(get_card_data_path(), 'w') as f:
            f.write('{}')
create_necessairy_files()
create_data_strucure()
