from util.training_data.fetch_data import synergy_gatherer
print()
synergy_gatherer.get_synergies(threads=201, save_interval=100, number_of_decks=1000, fetched_data_name='final_test')
#create_new_model.create_new_card_model(1, 'full_import.json', threads=250, max_training_data_entries=250, name='testing_model')