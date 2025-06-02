import util.json_util as json_util

def get_array(card_item, type, **weights):
    if type == 1:
        array = np_array_1(card_item)
    else:
        array = None
        print('type not supported')
        quit()
    array_data = {'type':type, 'weights':weights, 'array':array}
    return array_data



def categorise(string, category, ask_for_categorys = False):
    categorising_data = json_util.get_data('categories_1.json', ['machine_learning','categorising_data'])
    if category not in categorising_data:
        categorising_data[category] = {}

    if string not in categorising_data[category]:
        if ask_for_categorys:
            for key, item in categorising_data[category].items():
                print(f'{key}: {item}')
            print(category)
            try:
                input_category = input(f'choose category for "{string}": ')
            except:
                len(categorising_data[category]) + 1
            categorising_data[category][string] = int(input_category)
        else:
            categorising_data[category][string] = len(categorising_data[category]) +1
        json_util.dump_data('categories_1.json',categorising_data, ['machine_learning','categorising_data'])
    return categorising_data[category][string]

def get_combined_attribute(card_item, attribute):
    if hasattr(card_item, attribute):
        return getattr(card_item, attribute)
    elif hasattr(card_item, 'card_faces'):
        values = []
        for i in card_item.card_faces:
            if attribute in card_item.card_faces[i]:
                attribute_1_value =


def np_array_1(card_item, **weights):
        array = []

        # cmc

        cmc = card_item.cmc
        array.append(cmc)

        # pips

        colored_pips = card_item.mana_cost.count('{')
        array.append(colored_pips)

        # color_idendity

        color_idendity_string = ''.join(card_item.color_identity)
        color_idendity = categorise(color_idendity_string, 'color_idendity')
        array.append(color_idendity)

        # typeline

        typeline = card_item.type_line

        # supertypes

        array.append(int('Legendary' in typeline))

        # card_types

        split_typeline = typeline.split('—')
        card_types = split_typeline[0].split(' ')

        if card_types[0] == 'Legendary':
            card_types = card_types[1:]
        for i in range(3):
            if i < len(card_types):
                card_type = card_types[i]
                card_type = categorise(card_type, 'card_types')
                array.append(card_type)
            else:
                array.append(-1)

        # subtypes

        if len(split_typeline) < 1:
            subtypes = split_typeline[1].split(' ')
        else:
            subtypes = []
        for i in range(3):
            if i < len(subtypes):
                subtype = subtypes[i]
                subtype = categorise(subtypes, 'subtypes')
                array.append(subtype)
            else:
                array.append(-1)

        # power/toughness

        if hasattr(card_item, 'power'):
            array.append(card_item.power)
        else:
            array.append(-1)
        if hasattr(card_item, 'toughness'):
            array.append(card_item.toughness)
        else:
            array.append(-1)
        # edhrec_rank


        if hasattr(card_item, 'edhrec_rank'):
            array.append(card_item.edhrec_rank)
        else:
            array.append(36000)

        # keywords

        card_keywords = card_item.keywords
        for i in range(3):
            if i < len(card_keywords):
                card_keyword = card_keywords[i]
                card_keyword = categorise(card_keyword, 'keywords', False)
                array.append(card_keyword)
            else:
                array.append(-1)

        # salt score

        if hasattr(card_item, 'salt'):
            array.append(card_item.salt)
        else:
            array.append(-1)

        # layout

        array.append(categorise(card_item.layout, 'layout'))

        # rarity

        rarity = card_item.rarity
        rarity_category = categorise(rarity, 'rarity', True)
        array.append(rarity_category)

        # gamechanger

        if hasattr(card_item, 'game_changer') and card_item.game_changer:
            array.append(1)
        else:
            array.append(0)

        # oracle text

        oracle_text_list = card_item.oracle_text.split(' ')
        for i in range(60):
            if i < len(oracle_text_list):
                oracle_text = oracle_text_list[i]
                oracle_text_int = categorise(oracle_text, 'oracle_text', False)
                array.append(oracle_text_int)
            else:
                array.append(-1)
        return array



