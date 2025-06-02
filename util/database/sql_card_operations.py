from util.database import sql_util
import json

def get_card_dict(search_params:dict):
    cursor = sql_util.get_cursor()
    connector = cursor[0]
    cursor = cursor[1]

    # direct search
    query = 'SELECT json FROM cards WHERE ' + ' AND '.join([f'{key}=?' for key in search_params])
    params = tuple(search_params.values())
    # double sided cards
    if 'name' in search_params:
        query = query + f' OR (name Like ? and name LIKE \'%//%\') '
        params = params + ("%"+search_params["name"]+"%",)

    cursor.execute(query, params)
    card_dict_string = cursor.fetchone()
    if card_dict_string:
        connector.close()
        card_dict = json.loads(card_dict_string[0])
        return card_dict
    # FTS search
    search_conditions = []
    for key, value in search_params.items():
        # Escape quotes in value for FTS5 syntax
        if isinstance(value, bool):
            search_conditions.append(f'{key}')
        else:
            escaped_value = value.replace('"', '""')
            search_conditions.append(f'{key}:"{escaped_value}"')

    search_query = " AND ".join(search_conditions) if search_conditions else ""

    if not search_query:
        connector.close()
        return False
    query = ("\n"
             "                   SELECT cards.json\n"
             "                   FROM cards\n"
             "                            JOIN cards_fts ON cards.rowid = cards_fts.rowid\n"
             "                   WHERE cards_fts MATCH ? LIMIT 1\n"
             "                   ")
    cursor.execute(query, (search_query,))


    card_dict_string = cursor.fetchone()
    if not card_dict_string:
        connector.close()
        return False
    card_dict = json.loads(card_dict_string[0])
    connector.close()
    return card_dict

def update_card(card_dict:dict):
    cursor = sql_util.get_cursor()
    connector = cursor[0]
    cursor = cursor[1]
    if 'card_faces' in card_dict:
        cmc_front = card_dict['card_faces'][0]['cmc'] if 'cmc' in card_dict['card_faces'][0] else None
        cmc_back = card_dict['card_faces'][1]['cmc'] if 'cmc' in card_dict['card_faces'][1] else None
        oracle_text_front = card_dict['card_faces'][0]['oracle_text'] if 'oracle_text' in card_dict['card_faces'][
            0] else None
        oracle_text_back = card_dict['card_faces'][1]['oracle_text'] if 'oracle_text' in card_dict['card_faces'][
            1] else None
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
    connector.commit()
    connector.close()

def get_all_cards_by_query(query:str, params=None, table='cards.db'):
    cursor = sql_util.get_cursor(filename=table)
    connector = cursor[0]
    cursor = cursor[1]

    cursor.execute(query,params)
    card_dict_string = cursor.fetchall()
    return card_dict_string

