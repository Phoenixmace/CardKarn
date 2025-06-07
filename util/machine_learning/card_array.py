import util.data_util.json_util as json_util

def get_array(card_item, type, **weights):
    if type == 1:
        array = np_array_1(card_item,**weights)
    else:
        array = None
        print('type not supported')
        quit()
    array_data = {'type':type, 'weights':weights, 'array':array}
    return array_data



def categorise(string, category, categorising_data, ask_for_categorys = False):
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
    return categorising_data[category][string]

def get_combined_attribute(card_item, attribute):
    if hasattr(card_item, attribute):
        return getattr(card_item, attribute)
    elif hasattr(card_item, 'card_faces'):
        values = []
        for i in card_item.card_faces:
            if attribute in i:
                values.append(i[attribute])
        if len(values) == 1:
            return values[0]
        elif len(values) == 2:
            # combine
            if attribute == 'cmc':
                return sum(values) / len(values)

            elif attribute == 'mana_cost':
                return values[0]
            elif attribute == 'oracle_text':
                return ' // '.join(values)
            # typeline
            elif attribute == 'type_line':
                split_typeline_1 = values[0].split(' — ')
                split_typeline_2 = values[1].split(' — ')
                types = split_typeline_1[0] + ' ' + split_typeline_2[0]
                subtypes = []
                if len(split_typeline_1) == 2:
                    subtypes.append(split_typeline_1[1])
                if len(split_typeline_2) == 2:
                    subtypes.append(split_typeline_2[1])
                subtypes = ' '.join(subtypes)
                return types + ' — ' + subtypes

            elif attribute == 'power' or attribute == 'toughness':
                values = [int(i) for i in values]
                return sum(values) / len(values)
            elif isinstance(values[0], str):
                return ' // '.join(values)
            elif isinstance(values[0], int) or isinstance(values[0], float):
                return sum(values) / len(values)
            else:
                return values[0]


        else:
            return None

    else:
        return None

def np_array_1(card_item,**weights):
    categorising_data = json_util.get_shared_data('categories_1.json', ['machine_learning', 'categorising_data'])
    array = []
    # cmc


    cmc = get_combined_attribute(card_item, 'cmc')
    array.append(cmc)

    # pips

    pips = get_combined_attribute(card_item, 'mana_cost')
    colored_pips = pips.count('{')
    array.append(colored_pips)

    # color_idendity

    color_idendity_string = ''.join(card_item.color_identity)
    color_idendity = categorise(color_idendity_string, 'color_idendity',categorising_data)
    array.append(color_idendity)

    # typeline

    typeline = get_combined_attribute(card_item, 'type_line')

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
            card_type = categorise(card_type, 'card_types',categorising_data)
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
            subtype = categorise(subtypes, 'subtypes',categorising_data)
            array.append(subtype)
        else:
            array.append(-1)

    # power/toughness
    power = get_combined_attribute(card_item, 'power')
    if isinstance(power, int):
        array.append(power)
    else:
        array.append(-1)
    toughness = get_combined_attribute(card_item, 'toughness')
    if isinstance(toughness, int):
        array.append(toughness)
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
            card_keyword = categorise(card_keyword, 'keywords', categorising_data,False)
            array.append(card_keyword)
        else:
            array.append(-1)

    # salt score

    if hasattr(card_item, 'salt'):
        array.append(card_item.salt)
    else:
        array.append(-1)

    # layout

    array.append(categorise(card_item.layout, 'layout',categorising_data))

    # rarity

    rarity = card_item.rarity
    rarity_category = categorise(rarity, 'rarity',categorising_data, False)
    array.append(rarity_category)

    # gamechanger

    if hasattr(card_item, 'game_changer') and card_item.game_changer:
        array.append(1)
    else:
        array.append(0)

    # oracle text

    oracle_text = get_combined_attribute(card_item, 'oracle_text')
    oracle_text_list = oracle_text.split(' ')
    cleaned_oracle_text_list = []
    for string in oracle_text_list:
        for substring in string.split('\n'):
            cleaned_oracle_text_list.append(substring)

    for i in range(60):
        if i < len(cleaned_oracle_text_list):
            oracle_text = cleaned_oracle_text_list[i]
            oracle_text_int = categorise(oracle_text, 'oracle_text',categorising_data, False)
            array.append(oracle_text_int)
        else:
            array.append(-1)
    json_util.update_shared_data('categories_1.json', categorising_data, ['machine_learning', 'categorising_data'])
    return array



