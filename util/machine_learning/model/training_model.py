import json
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from util.database.sql_card_operations import get_all_cards_by_query
import numpy
import ast
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense, Concatenate
from tensorflow.keras.models import Model
from tqdm import tqdm
import codecs

def train_model(model_name, final_training_data_path,save_dataset_path, oracle_tokenizer_name='oracle_tokenizer', card_tokenizer_name='card_tokenizer', model_save_path=r"C:\Users\maxce\Shared Folder\Code\Maturaarbeit\data_folder\neural_network\models", dataset_amount=1):
    binary_training_data_path = os.path.join(final_training_data_path, 'binary.json')
    adjusted_binary_training_data_path = os.path.join(final_training_data_path, 'adjusted_binary.json')

    # get all arrays
    array_dict = {}
    query = "SELECT oracle_id_front, oracle_id_back, tokens FROM cards where tokens not null"
    all_cards = get_all_cards_by_query(query)
    for oracle_id_front, oracle_id_back, tokens in tqdm(all_cards, desc='getting all arrays'):
        if tokens == None:
            print(oracle_id_front, oracle_id_back, tokens, 'no tokens found')
        if tokens:
            for oracle_side_id in [oracle_id_back, oracle_id_front]:
                if oracle_side_id and oracle_side_id not in array_dict:
                    array_dict[oracle_side_id] = tokens
    def prepare_inputs(filepath, save_dataset_full_path):
        card_1_inputs = []
        card_2_inputs = []
        outputs = []
        raw_data = json.load(open(filepath, 'r'))
        raw_inputs = raw_data['inputs']
        raw_outputs = raw_data['outputs']
        if len(raw_inputs) != len(raw_outputs):
            print('invalid dataset')
            quit()
        failed_iterations = 0
        for i in tqdm(range(int(len(raw_inputs)*dataset_amount)), desc='preparing inputs'):
            if len(card_1_inputs) != len(card_2_inputs) or len(card_1_inputs) != len(outputs):
                print('shortening arrays for data validity')
                outputs = outputs[:i-5]
                card_1_inputs = card_1_inputs[:i-5]
                card_2_inputs = card_2_inputs[:i-5]
            try:
                index = i-1
                output = raw_outputs[index]
                raw_input = raw_inputs[index]
                cards = raw_input[0]
                card_1_oracle_id = cards[0]
                card_2_oracle_id = cards[1]

                card_1_tokens = array_dict.get(card_1_oracle_id)
                card_2_tokens = array_dict.get(card_2_oracle_id)

                if card_1_tokens is None or card_2_tokens is None:
                    failed_iterations +=1
                    #print(f"{round(100*(failed_iterations/i), 2)}% of iterations failed")
                    continue  # skip this iteration

                card_1_nested_list = ast.literal_eval(card_1_tokens)
                card_2_nested_list = ast.literal_eval(card_2_tokens)

                card_1_array_2d = numpy.array(card_1_nested_list, dtype=int)
                card_2_array_2d = numpy.array(card_2_nested_list, dtype=int)
                if isinstance(card_2_array_2d,numpy.ndarray) and isinstance(card_1_array_2d,numpy.ndarray) and output != None:
                    card_1_inputs.append(card_1_array_2d)
                    card_2_inputs.append(card_2_array_2d)
                    outputs.append(output)
            except Exception as e:
                print(e)
                #quit()
        print(f"{round(100 * (failed_iterations / int(len(raw_inputs)*dataset_amount)), 2)}% of iterations failed")
        card_1_json_inputs = [card_input.tolist() for card_input in card_1_inputs]
        card_2_json_inputs = [card_input.tolist() for card_input in card_2_inputs]
        print('dumping converted dataset...')
        json.dump({'card_1_inputs': card_1_json_inputs, 'card_2_inputs':card_2_json_inputs, 'outputs': outputs}, codecs.open(save_dataset_full_path, 'w'), indent=4)
        return card_1_inputs, card_2_inputs, outputs
    binary_card_1_inputs, binary_card_2_inputs, binary_outputs = prepare_inputs(binary_training_data_path, os.path.join(save_dataset_path, 'binary.json'))
    adjusted_card_1_inputs, adjusted_card_2_inputs, adjusted_outputs = prepare_inputs(adjusted_binary_training_data_path, os.path.join(save_dataset_path, 'adjusted_binary.json'))

    def create_model(card_1_inputs, card_2_inputs, outputs, model_name, oracle_tokenizer_name, card_tokenizer_name):
        X1 = numpy.array(card_1_inputs)  # shape: (samples, 50)
        X2 = numpy.array(card_2_inputs)  # shape: (samples, 50)
        y = numpy.array(outputs).astype('float32')  # shape: (samples,

        input1 = Input(shape=(50,), name="card_1_input")
        input2 = Input(shape=(50,), name="card_2_input")

        # Shared embedding layer
        embedding_layer = Embedding(input_dim=3000, output_dim=64, name="shared_embedding")

        # Embed both inputs
        embedded1 = embedding_layer(input1)  # shape: (batch, 50, embedding_dim)
        embedded2 = embedding_layer(input2)

        # Process with LSTM (can be replaced with Flatten, GlobalAvgPool, etc.)
        lstm1 = LSTM(32)(embedded1)
        lstm2 = LSTM(32)(embedded2)

        # Concatenate both outputs
        merged = Concatenate()([lstm1, lstm2])

        # Dense layers for regression
        dense = Dense(64, activation='relu')(merged)
        output = Dense(1, name="synergy_output")(dense)  # Output is a float

        model = Model(inputs=[input1, input2], outputs=output)
        model.compile(optimizer='adam', loss='mse')

        return model
    binary_model = create_model(binary_card_1_inputs, binary_card_2_inputs, binary_outputs, model_name, oracle_tokenizer_name, card_tokenizer_name)
    adjusted_binary_model = create_model(adjusted_card_1_inputs, adjusted_card_2_inputs, adjusted_outputs, model_name, oracle_tokenizer_name, card_tokenizer_name)

    def train_model(model, card_1_inputs, card_2_inputs, outputs, model_name, batch_size=32, epochs=10, validation_split=0.1):
        X1 = numpy.array(card_1_inputs).squeeze(1)  # -> shape (samples, 50)
        X2 = numpy.array(card_2_inputs).squeeze(1)  # -> shape (samples, 50)
        y = numpy.array(outputs).astype('float32')  # shape: (samples,

        X1 = numpy.array(X1).reshape(-1, 50)  # if each input should have 50 tokens
        X2 = numpy.array(X2).reshape(-1, 50)

        assert X1.shape == X2.shape, "Card inputs must have same shape"
        assert len(X1) == len(y), "Inputs and outputs must have same number of samples"

        model.fit([X1, X2],y, batch_size=batch_size, epochs=epochs, validation_split=validation_split, verbose=1, shuffle=True)
        save_path = os.path.join(model_save_path, f'{model_name}.h5')
        model.save(save_path)

        # testing
        synergy_testing_names = [
            ['Temur Sabertooth','Zacama, Primal Calamity'],
            ['Ratadrabik of Urborg','Blade of Shared Souls'],
            ['Midnight Guard','Presence of Gond'],
            ['Yarok, the Desecrated', 'Dimir Aqueduct'],
            ['Niv-Mizzet, Parun', 'Curiosity'],
            ['Collector Ouphe', 'Basalt Monolith']
        ]
        X1_test = []
        X2_test = []
        for pair in synergy_testing_names:
            # x1
            query = f"select tokens from cards where name = \"{pair[0]}\""
            card = get_all_cards_by_query(query)[0]
            card_string = card[0] if isinstance(card, tuple) else card
            card_nested_list = ast.literal_eval(card_string)
            card_array_2d = numpy.array(card_nested_list, dtype=int)
            # x2
            query = f"select tokens from cards where name = \"{pair[1]}\""
            card_2 = get_all_cards_by_query(query)[0]
            card_2_string = card_2[0] if isinstance(card_2, tuple) else card_2
            card_2_nested_list = ast.literal_eval(card_2_string)
            card_2_array_2d = numpy.array(card_2_nested_list, dtype=int)
            print(type(card_2_array_2d), type(card_array_2d))
            if isinstance(card_2_array_2d,numpy.ndarray) and isinstance(card_array_2d, numpy.ndarray) != None:
                X1_test.append(card_array_2d)
                X2_test.append(card_2_array_2d)

        X1_test = numpy.array(X1_test)  # shape: (samples, 50)
        X2_test = numpy.array(X2_test)

        X2_test = numpy.array(X2_test).reshape(-1, 50)  # if each input should have 50 tokens
        X1_test = numpy.array(X1_test).reshape(-1, 50)

        predictions = model.predict([X1_test, X2_test])

        # Compare with actual
        for i in range(len(synergy_testing_names)):  # preview first 5
            print(f"Predicted Synergy of {synergy_testing_names[i][0]} + {synergy_testing_names[i][1]}: {predictions[i][0]:.4f}")

    train_model(binary_model, binary_card_1_inputs, binary_card_2_inputs, binary_outputs, f'binary_{model_name}', batch_size=32, epochs=10, validation_split=0.1)
    train_model(adjusted_binary_model, adjusted_card_1_inputs, adjusted_card_2_inputs, adjusted_outputs, f'adjusted_binary_{model_name}', batch_size=32, epochs=10, validation_split=0.1)