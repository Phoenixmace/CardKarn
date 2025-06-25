from util.training_data.fetch_data import synergy_gatherer
synergy_gatherer.get_synergies(threads=350, save_interval=5000, number_of_decks=10000, fetched_data_name='10k_param_test')
#create_new_model.create_new_card_model(1, 'full_import.json', threads=250, max_training_data_entries=250, name='testing_model')