import numpy as np
from util.data_util.json_util import get_data, dump_data
import tensorflow as tf
from models.Card import BaseCard
def train_card_model(training_data_file_name:str):
    card_training_data = get_data(training_data_file_name, subfolder=['machine_learning', 'final_training_data'])
    card = np.array(card_training_data['input'])
    synergy = np.array(card_training_data['key'])

    model = tf.keras.Sequential([
        tf.keras.layers.Dense(128, activation='relu', input_shape=(card.shape[1],)),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(card, synergy, epochs=10, batch_size=32)

    # test synergy
    new_card1 = BaseCard({'name':'Thassa\s Oracle'}).get_np_array()
    new_card2 = BaseCard({'name':'Tainted Pact'}).get_np_array()
    new_input = np.concatenate([new_card1, new_card2])
    prediction = model.predict(np.array([new_input]))
    print("Predicted synergy:", prediction[0][0])
train_card_model('testing_dataset.json')






