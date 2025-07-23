import os
from util.data_util.data_util import get_data_path
import pickle
import numpy
try:
    from tensorflow.keras.preprocessing.sequence import pad_sequences
except:
    try:
        from keras.api.preprocessing.sequence import pad_sequences as pad_sequences
    except:
        print('Could not import tf')
        exit()

def tokenize_oracle_text(card, model_name):
    tokenizer_path = get_data_path(f'{model_name}.pickle', ['neural_network', 'tokenizers'], allow_not_existing=True)
    if not os.path.exists(tokenizer_path):
        print('invalid tokenizer', model_name)
        return
    tokenizer = pickle.load(open(tokenizer_path, 'rb'))

    # get oracle text
    if hasattr(card, 'card_faces'):
        oracle_text = []
        for face in card.card_faces:
            if 'oracle_text' in face:
                oracle_text.append(face['oracle_text'])
        oracle_text = ' // '.join(oracle_text)
    else:
        oracle_text = card.oracle_text

    oracle_tokens = tokenizer.texts_to_sequences([oracle_text])
    return oracle_tokens

def tokenize_general_card(card, oracle_tokenizer_name):
    tokenizer_path = get_data_path(f'{oracle_tokenizer_name}.pickle', ['neural_network', 'tokenizers'], allow_not_existing=True)
    if not os.path.exists(tokenizer_path):
        print('invalid tokenizer: ', oracle_tokenizer_name)
        return
    tokenizer = pickle.load(open(tokenizer_path, 'rb'))
    def create_card_strin(card):
        rarity = card.rarity
        layout = card.layout
        if hasattr(card, 'card_faces'):
            def combine_texts(card_faces, key):
                texts = []
                for face in card_faces:
                    if key in face:
                        texts.append(face[key])
                return ' // '.join(texts)
            mana_cost = combine_texts(card.card_faces, 'mana_cost')
            type_line = combine_texts(card.card_faces, 'type_line')
        else:
            mana_cost = card.mana_cost
            type_line = card.type_line
        string = [rarity, layout, mana_cost, type_line]
        string = ", ".join(string)
        return string
    card_string = create_card_strin(card)
    card_tokens = tokenizer.texts_to_sequences([card_string])

    # other attributes
    other_attributes = []
    colors = ['B', 'U', 'G', 'R', 'W']
    for color in colors:
        if color in card.color_identity:
            other_attributes.append(1)
        else:
            other_attributes.append(0)

    if hasattr(card, 'power') and isinstance(card.power, str):
        try:
            other_attributes.append(int(card.power))
        except:
            other_attributes.append(0)
    else:
        other_attributes.append(0)

    if hasattr(card, 'toughness') and isinstance(card.toughness, str):
        try:
            other_attributes.append(int(card.toughness))
        except:
            other_attributes.append(0)
    else:
        other_attributes.append(0)

    if hasattr(card, 'game_changer') and card.game_changer:
        other_attributes.append(1)
    else:
        other_attributes.append(0)
    for attribute in other_attributes:
        card_tokens = numpy.append(card_tokens, attribute)
    # other attributes
    return card_tokens



def tokenize_card(card, name='tokenizer', card_model_name=None, padding_max_oracle_length=25, oracle_tokenizer_name=None, padding_max_card_length=25):
    if not isinstance(card_model_name, str):
        card_model_name = f'card_{name}'
    if not isinstance(oracle_tokenizer_name, str):
        oracle_tokenizer_name = f'oracle_{name}'
    if hasattr(card, 'tokenized') and name in card.tokenized:
        return card.tokenized[name]
    else:
        oracle_tokens = tokenize_oracle_text(card, oracle_tokenizer_name)[0]
        card_tokens = tokenize_general_card(card, card_model_name)
        padded_oracle = pad_sequences([oracle_tokens], maxlen=padding_max_oracle_length)  # choose a consistent MAX_LEN
        padded_card = pad_sequences([card_tokens], maxlen=padding_max_card_length)
        # choose a consistent MAX_LEN

        return padded_oracle, padded_card

