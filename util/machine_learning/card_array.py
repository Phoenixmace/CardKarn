import util.json_util as json_util

def get_array(card_item, type, **weights):
    if type == '1':
        array = simple_array(card_item)
    else:
        array = None
        print('type not supported')
        quit()
    array_data = {'type':type, 'weights':weights, 'array':array}
    return array_data



def categorise(string, category, ask_for_categorys = False):
    categorising_data = json_util.get_data('model_1.json', ['machine_learning','categorising_data'])
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
        json_util.dump_data('model_1.json',categorising_data, ['machine_learning','categorising_data'])
    return categorising_data[category][string]

def simple_oracle_text(string, ask_word_input = True):
    # get deletion_words
    categorising_data = json_util.get_data('model_1.json', ['machine_learning','categorising_data'])
    if 'oracle_words' not in categorising_data:
        categorising_data['oracle_words'] = {}

    # label words

    string = string.lower()
    string = string.replace('this creature', 'card_name')
    word_list = string.split(' ')
    word_array = []
    for word in word_list:
        if word not in categorising_data['oracle_words']:
            if ask_word_input:
                input_word = input(f'is "{word}" a word to delete? (enter to keep): ')
                if len(input_word) > 0:
                    categorising_data['oracle_words'][word] = False
                else:
                    categorising_data['oracle_words'][word] = len(categorising_data['oracle_words']) +1
        if categorising_data['oracle_words'][word]:
            word_array.append(word)
    json_util.dump_data('model_1.json', categorising_data, ['machine_learning','categorising_data'])

    return word_array


def simple_array(card_item,**weights):
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
                array.append(subtypes)
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

        array.append(card_item.edhrec_rank)

        # keywords

        card_keywords = card_item.keywords
        for i in range(3):
            if i < len(card_keywords):
                card_keyword = card_keywords[i]
                card_keyword = categorise(card_keyword, 'keywords', True)
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

        if card_item.game_changer:
            array.append(1)
        else:
            array.append(0)

        # oracle text

        oracle_text_list = simple_oracle_text(card_item.oracle_text)
        for i in range(100):
            if i < len(oracle_text_list):
                oracle_text = oracle_text_list[i]
                oracle_text = categorise(oracle_text, 'oracle_text', False)
                array.append(oracle_text)
            else:
                array.append(-1)
        return array



