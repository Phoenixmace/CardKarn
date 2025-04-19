import ijson
from util import json_util
return_dict = {}

def get_generators(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        parser = ijson.items(f, 'item')
        a = {str(obj.get('name', f'unnamed_{index}')).lower(): index for index, obj in enumerate(parser)}
        return a
# r'C:\Users\maxce\Downloads\default-cards-20250418090919.json'
def index_database(path):
    generators = get_generators(path)
    json_util.dump_data('card_database.json', generators)