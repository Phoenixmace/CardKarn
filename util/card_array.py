
def get_int_from_str(characteristic, card_object):
    return card_object
def convert(characteristic, card_object):
    pass
def get_color(characteristic, card_object):
    pass
def get_oracle_array(characteristic, card_object):
    pass


def simple_array(card_item,**weights):
        # default weights, value
        defaults = [
            {
                'name': 'released_at',
                'value': 15,
                'weight': 1,
                'function': get_int_from_str,
                'data_path': ['released_at']
            },
            {
                'name': 'cmc',
                'value': -1,
                'weight': 1,
                'function': convert,
                'data_path': ['cmc']
            },
            {
                'name': 'colored_pips',
                'value': -1,
                'weight': 1,
                'function': get_color,  # assuming get_color returns a list or count
                'data_path': ['mana_cost']  # index 1 = number of colored pips
            },
            {
                'name': 'color_identity',
                'value': -1,
                'weight': 1,
                'function': get_int_from_str,
                'data_path': ['color_identity', 'color_identity']
            },
            {
                'name': 'card_types',
                'value': -1,
                'weight': 1,
                'function': get_int_from_str,
                'data_path': ['type_line', 'type']  # assumes split or preprocessed
            },
            {
                'name': 'layout',
                'value': -1,
                'weight': 1,
                'function': get_int_from_str,
                'data_path': ['layout', 'layout']
            },
            {
                'name': 'oracle_text',
                'value': -1,
                'weight': 1,
                'function': get_oracle_array,
                'data_path': ['oracle_text']
            },
            {
                'name': 'keywords',
                'value': -1,
                'weight': 1,
                'function': get_int_from_str,
                'data_path': ['keywords', 'keyword']  # each keyword separately
            },
            {
                'name': 'game_changer',
                'value': 0,
                'weight': 1,
                'function': convert,
                'data_path': ['game_changer']
            },
            {
                'name': 'rarity',
                'value': -1,
                'weight': 1,
                'function': get_int_from_str,
                'data_path': ['rarity', 'rarity']
            },
            {
                'name': 'price',
                'value': -1,
                'weight': 1,
                'function': convert,
                'data_path': ['prices', 'eur']
            },
            {
                'name': 'salt',
                'value': -1,
                'weight': 1,
                'function': convert,
                'data_path': ['salt']
            },
            {
                'name': 'edhrec_rank',
                'value': -1,
                'weight': 1,
                'function': convert,
                'data_path': ['edhrec_rank']
            }
        ]

        # Override defaults with any provided kwargs
        weights.update(weights)

        # get characteristics
        for characteristic in defaults:
            # get value
            value = card_item.__dict__
            for step in characteristic['data_path']:
                if step in value:
                    value = value[step]
                else:
                    value = None

            if value:
                processed = characteristic['function'](characteristic, value)
            else:
                processed = characteristic['value']
            #weighted = processed * characteristic['weight']
            print(f"{characteristic['name']}: {processed}")


def get_array(card_item, type, **weights):
    if type == 'simple':
        array = simple_array(card_item)
    else:
        array = None
        print('type not supported')
        quit()
    array_data = {'type':type, 'weights':weights, 'array':array}
    return array_data
