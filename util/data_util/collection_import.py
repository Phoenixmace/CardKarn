import csv

import config
from util.data_util import json_util
import os
import sqlite3
from util.database import sql_util

def import_collection_from_manabox(file_path, add_lists=False, user_id=1):
    file_path = file_path.replace('\\', '/')
    # import each card
    db_path = os.path.join(config.data_folder_path, 'sql', 'user_tables', f'{user_id}.db')

    con = sqlite3.connect(db_path)
    cursor = con.cursor()

    query = '''
    CREATE TABLE IF NOT EXISTS collection
    (
        scryfall_id
        TEXT
        PRIMARY
        KEY,
        quantity INTEGER,
        collector_number TEXT,
        is_foil BOOLEAN,
        purchase_price TEXT,
        misprint BOOLEAN,
        altered BOOLEAN,
        condition TEXT,
        language TEXT
    )'''
    cursor.execute(query)
    con.commit()

    with open(file_path, newline='') as csvfile:
        csv_data = csv.reader(csvfile, delimiter=',', quotechar='"')
        is_first_row = True
        params = []
        for row in csv_data:
            if is_first_row:
                is_first_row = False
                continue
            card_id = row[10]
            collector_number = row[5]
            is_foil = bool(row[6])
            quantity = int(row[8])
            purchase_price = row[11]
            misprint = bool(row[12])
            altered = bool(row[13])
            condition = row[14]
            language = row[15]

            params.append((card_id, quantity, collector_number, is_foil, purchase_price, misprint, altered, condition, language))

        query = '''
        INSERT OR REPLACE INTO collection (scryfall_id, quantity, collector_number, is_foil, purchase_price, misprint, altered, condition, language)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        cursor.executemany(query, params)
        con.commit()
        con.close()


import_collection_from_manabox(r"C:\Users\maxce\Downloads\ManaBox_Collection_für_ma.csv", add_lists=True)