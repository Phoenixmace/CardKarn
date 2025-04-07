from time import sleep
import requests
import csv
from models.Card import Card

def import_an_array_of_cards(cards):#[**kwargs must have name, ] only name set_code, finish language
    search_query = 'https://api.scryfall.com/cards/search?q='

    attribute_syntax_dict = {'set_code': 'set',
                             'finish':'is',
                             'language':'lang',
                             'name':'name'
                             }
    validation_list = []
    for card in cards:
        card_query = f'('
        for attribute in card:
            card_query = card_query + f'{attribute_syntax_dict[attribute]}:\"{card[attribute]}\" '
        card_query = card_query + ') OR '
        search_query = search_query + card_query
        validation_list.append(card['name'])
    del cards

    print(search_query[:-4])
    response = requests.get(search_query)
    if response.status_code == 200:
        return_dict = response.json()
    else:
        print('something went wrong')
        return False
    return_list = []
    for card in return_dict['data']:
        validation_list.remove(card['name'])
        return_list.append(Card(card['name'], with_existing_scryfall=card))
    print(f'those cards were not found {validation_list}')
    return return_list

    print()
def import_collection_from_manabox(file_path, add_lists=False, all_main=False):
    file_path = file_path.replace('\\', '/')
    # get length
    with open(file_path, newline='') as csvfile:
        csv_data = csv.reader(csvfile, delimiter=',', quotechar='"')
        max_imports =sum(1 for row in csv_data)
    # import each card
    with open(file_path, newline='') as csvfile:
        csv_data = csv.reader(csvfile, delimiter=',', quotechar='"')
        print(max_imports)
        count = 1
        for row in csv_data:
            if (row[1] == 'binder' or add_lists) and row[2] != 'Name':
                if row[1] == 'deck' or all_main:
                    target = 'main'
                else:
                    target = row[0]
                if row[6] == 'normal':
                    finish = 'nonfoil'
                else:
                    finish = row[6]
                card = Card(name=row[2], number=row[8], set_code=row[3], finish=finish, language=row[15], no_setcode_required=False)
                if card.is_valid:
                    card.save_old(False, subfolder=target, del_after=True)
                    print(f'{round(count / max_imports * 100, 1)}%')
                else:
                    print(row[2], 'could not be loaded')
                sleep(0.05)
                count += 1

print(import_an_array_of_cards([{'name': 'Archmage Emeritus', 'set_code': 'stx'}, {'name': 'Time Warp'}]))