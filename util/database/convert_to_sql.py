import sqlite3
from util import data_util, json_util
import json

from util.database.sql_util import get_cursor




def init_db(filename='cards.db'):
    cursor = get_cursor(filename)
    connector = cursor[0]
    cursor = cursor[1]

    # create database
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cards
    (
        scryfall_id
        TEXT
        PRIMARY
        KEY,
        name
        TEXT,
        cmc_front
        REAL,
        cmc_back
        REAL,
        type_line_front
        TEXT,
        type_line_back
        TEXT,
        oracle_text_front
        TEXT,
        oracle_text_back 
        TEXT,
        rarity
        TEXT,
        edhrec_rank
        INTEGER,
        salt
        REAL,
        price_eur
        REAL,
        json
        TEXT,
        oracle_id_front
        TEXT,
        oracle_id_back
        TEXT,
        commander_legal
        BOOLEAN,
        -- color_identity
        green_in_color_identity BOOLEAN,
        red_in_color_identity BOOLEAN,
        blue_in_color_identity BOOLEAN,
        white_in_color_identity BOOLEAN,
        black_in_color_identity BOOLEAN,
        layout TEXT,
        double_faced_card BOOLEAN,
        set TEXT
        
    )''')

    # insert values
    with open(data_util.get_data_path("card_database.json", subfolder='database'), "r", encoding="utf-8") as f:
        lines = f.readlines()
        line_number = 0
        num_lines = len(lines)
        for line in lines:
            line_number += 1
            print(f"importing database: {round(100*lines.index(line)/num_lines,2)}%")
            if '{' in line:

                formatted_line = line.strip()[:line.rindex('}') + 1]
                card_dict = json.loads(formatted_line)
                # Extract and prepare values for SQL insertion
                if 'card_faces' in card_dict:
                    cmc_front = card_dict['card_faces'][0]['cmc'] if 'cmc' in card_dict['card_faces'][0] else None
                    cmc_back = card_dict['card_faces'][1]['cmc'] if 'cmc' in card_dict['card_faces'][1] else None
                    oracle_text_front = card_dict['card_faces'][0]['oracle_text'] if 'oracle_text' in card_dict['card_faces'][0] else None
                    oracle_text_back = card_dict['card_faces'][1]['oracle_text'] if 'oracle_text' in card_dict['card_faces'][1] else None
                    typeline_front = card_dict['card_faces'][0]['type_line'] if 'type_line' in card_dict['card_faces'][0] else None
                    typeline_back = card_dict['card_faces'][1]['type_line'] if 'type_line' in card_dict['card_faces'][1] else None
                    oracle_id_front = card_dict['card_faces'][0]['oracle_id'] if 'oracle_id' in card_dict['card_faces'][0] else None
                    oracle_id_back = card_dict['card_faces'][1]['oracle_id'] if 'oracle_id' in card_dict['card_faces'][1] else None
                else:
                    cmc_front = card_dict['cmc'] if 'cmc' in card_dict else None
                    cmc_back = None
                    oracle_text_front = card_dict['oracle_text'] if 'oracle_text' in card_dict else None
                    oracle_text_back = None
                    typeline_front = card_dict['type_line'] if 'type_line' in card_dict else None
                    typeline_back = None
                    oracle_id_front = card_dict['oracle_id'] if 'oracle_id' in card_dict else None
                    oracle_id_back = None
                values = {
                    'scryfall_id': card_dict['id'],
                    'name': card_dict['name'],
                    'cmc_front': cmc_front,
                    'cmc_back': cmc_back,
                    'type_line_front': typeline_front,
                    'type_line_back': typeline_back,
                    'oracle_text_front': oracle_text_front,
                    'oracle_text_back': oracle_text_back,
                    'rarity': card_dict['rarity'],
                    'edhrec_rank': card_dict.get('edhrec_rank'),  # safer to use get
                    'salt': card_dict.get('salt'),
                    'price_eur': card_dict.get('prices', {}).get('eur'),  # safer nested get
                    'json': json.dumps(card_dict),
                    'oracle_id_front': oracle_id_front,
                    'oracle_id_back': oracle_id_back,
                    'commander_legal': card_dict['legalities']['commander'] != 'not_legal',
                    'green_in_color_identity': 'G' in card_dict.get('color_identity', []),
                    'red_in_color_identity': 'R' in card_dict.get('color_identity', []),
                    'blue_in_color_identity': 'U' in card_dict.get('color_identity', []),
                    'white_in_color_identity': 'W' in card_dict.get('color_identity', []),
                    'black_in_color_identity': 'B' in card_dict.get('color_identity', []),
                    'layout': card_dict['layout'],
                    'double_faced_card': 'card_faces' in card_dict,
                }

                # insert values in sql
                keys = ', '.join(values.keys())
                placeholders = ', '.join('?' for _ in values)
                vals = tuple(values.values())

                sql = f"INSERT OR REPLACE INTO cards ({keys}) VALUES ({placeholders})"

                cursor.execute(sql, vals)
                if line_number % 1000 == 0:
                    connector.commit()
    connector.commit()
    connector.close()

init_db()