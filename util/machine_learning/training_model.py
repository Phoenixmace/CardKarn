import numpy as np

from util.data_util import data_util
from util.data_util.json_util import get_data, dump_data
import tensorflow as tf
from models.Card import BaseCard
def train_card_model(method_name:str, method, model_name):
    card_training_data = get_data(f'dataset_cards_{method_name}.json', subfolder=['machine_learning', f'model_{method_name}'])
    card = np.array(card_training_data['inputs'], dtype=np.float32)
    synergy = np.array(card_training_data['keys'])
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(128, activation='relu', input_shape=(card.shape[1],)),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='mse')
    early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    model.fit(card, synergy, epochs=30, batch_size=32, validation_split=0.2, callbacks=[early_stop])
    model_path = data_util.get_data_path(f'model_{model_name}.keras', subfolder=['machine_learning', f'model_{method_name}'], allow_not_existing=True)
    model.save(model_path)
    # test synergy
    print("\n\n\n\nTesting synergies:")
    pairs = [
        ['Thassa\'s Oracle', 'Tainted Pact'],
        ['Demonic Consultation', 'Thassa\'s Oracle'],
        ['Lightning Bolt', 'Snapcaster Mage'],
        ['Counterspell', 'Isochron Scepter'],
        ['Heliod, Sun-Crowned', 'Walking Ballista'],
        ['Saheeli Rai', 'Felidar Guardian'],
        ['Splinter Twin', 'Pestermite'],
        ['Kiki-Jiki, Mirror Breaker', 'Restoration Angel'],
        ['Dark Depths', 'Thespian\'s Stage'],
        ['Necrotic Ooze', 'Devoted Druid'],
        ['Mikaeus, the Unhallowed', 'Triskelion'],
        ['Griselbrand', 'Reanimate'],
        ['Urza, Lord High Artificer', 'Paradox Engine'],
        ['Skullclamp', 'Goblin Sharpshooter'],
        ['Aluren', 'Cavern Harpy']]
    for pair in pairs:

        new_card1 = BaseCard({'name':pair[1]}).get_np_array(method=method, load_existing=False, name=method_name, weights={})
        new_card2 = BaseCard({'name':pair[0]}).get_np_array(method=method, load_existing=False, name=method_name, weights={})
        arrays = sorted([new_card2, new_card1])
        arrays = arrays[0] + arrays[1]
        new_input = np.array([arrays])
        prediction = model.predict(new_input)
        print(f'{pair[0]} + {pair[1]}: ', prediction[0][0])








