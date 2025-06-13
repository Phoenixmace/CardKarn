from util.threading_util import ThreadingHandler
import requests
import threading
import time

def get_all_hashes(threads):
    commanders = get_all_commanders()
    hashes = []
    hashes_lock = threading.Lock()
    params = [(commander, hashes, hashes_lock) for commander in commanders[:1000]]
    handler = ThreadingHandler(threads)
    handler.start_process(params, add_all_hashes_by_commander, process_message='Fetching hashes')
    return hashes



def add_all_hashes_by_commander(commander, hashes, lock):
    url_end = clean_name(commander)
    url = f'https://json.edhrec.com/pages/decks/{url_end}.json'.lower()
    for i in range(2):
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            for index, key in enumerate(data['table']):
                lock.acquire()
                hashes.append(data['table'][index]['urlhash'])
                lock.release()
                return
        else:
            time.sleep(0.5)


def clean_name(name):
    if '//' in name:
        url_end = name.split('//')[0]  # idea for var name Luc
    else:
        url_end = name
    replace_char_dict = {
        'ó': 'o',
        ' ': '-',
        '!': '',
        ',': '',
        '\'': '',
    }
    for char in replace_char_dict:
        url_end = url_end.replace(char, replace_char_dict[char])
    return url_end
def get_all_commanders():
    # get data from all pages
    page = 1
    continute = True
    commanders = []
    while continute:
        try:
            url = f"""https://api.scryfall.com/cards/search?q=%28game%3Apaper%29+legal%3Acommander+is%3Acommander&order=none&unique=none&dir=none&include_variations=false&include_extras=false&include_multilingual=false&page={page}"""
            response = requests.get(url)
            data = response.json()
            for commander in data['data']:
                commander_name = commander['name']
                if commander_name not in commanders:
                    commanders.append(commander_name)
            page += 1

        except:
            continute = False
    return commanders