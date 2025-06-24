from website.backend.backend_util.images import card_images
from util.database.sql_util import get_cursor
from models.Card import BaseCard
import os
import json
def convert_collection_to_list(collection):
    card_list = []
    for row in collection.split('\n')[:50]:
        try:
            path = card_images.get_image_path(row.split(',')[10])
            card_object = BaseCard({'scryfall_id':row.split(',')[10]})
            if path and card_object:
                card_list.append({'id':path.split(os.sep)[-1], 'name':card_object.name, 'number': row.split(',')[8], 'rarity':card_object.rarity, 'color':card_object.color_identity[0], 'mana_value': card_object.cmc, 'price': card_object.prices['eur']})
        except Exception as e:
            print(e)
            pass
    return card_list