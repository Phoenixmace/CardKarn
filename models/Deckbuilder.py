import numpy as np
import keras
from keras.models import load_model
import os
import config

class Deckbuilder:
    def __init__(self, commander, budget, model_name, tag=None, tribe=None, card_weight=1):
        self.commander = commander
        self.budget = budget
        self.model_name = model_name
        self.tag = tag
        self.tribe = tribe

    def build_deck(self):
        # load model
        model_path = os.path.join(config.data_folder_path, 'neural_network', 'models', f'{self.model_name}.h5')
        if not os.path.exists(model_path):
            print('model not found')
            return
        model = load_model(model_path)


