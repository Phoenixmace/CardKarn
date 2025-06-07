import csv
from util.data_util import json_util


def import_collection_from_manabox(file_path, add_lists=False):
    file_path = file_path.replace('\\', '/')
    # import each card
    with open(file_path, newline='') as csvfile:
        csv_data = csv.reader(csvfile, delimiter=',', quotechar='"')
        collection = {}
        for row in csv_data:
            if (row[1] == 'binder' or add_lists) and row[2] != 'Name':
                collection[row[10]] = {'price':row[11], 'condition':row[14], 'language':row[15], 'quantity':row[8], 'foil':row[6]}
        json_util.dump_data('collection.json', data=collection)


import_collection_from_manabox(r"C:\Users\maxce\Downloads\ManaBox_Collection_für_ma.csv", add_lists=True)