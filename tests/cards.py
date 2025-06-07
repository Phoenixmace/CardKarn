from util.machine_learning.data_preparation_1 import create_training_arrays
from util.machine_learning import create_new_model


create_new_model.create_new_card_model(1, 'full_import.json', threads=250, max_training_data_entries=250, name='testing_model')