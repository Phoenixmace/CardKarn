import numpy as np
import tensorflow as tf
from models.Card import BaseCard


def evaluate_synergy(model_path, card_pairs):
    # Load model
    model = tf.keras.models.load_model(model_path)

    # Prepare model input arrays
    X1_oracle, X1_card = [], []
    X2_oracle, X2_card = [], []

    missing = 0
    for card_1_name, card_2_name in card_pairs:
        try:
            card_1_item = BaseCard({'name': card_1_name})
            card_2_item = BaseCard({'name': card_2_name})

            card1_oracle, card_1_card = card_1_item.get_np_array()  # shape (2, feature_dim)
            card2_oracle, card_2_card = card_2_item.get_np_array()  # shape (2, feature_dim)

            X1_oracle.append(card1_oracle)  # oracle tokens
            X1_card.append(card_1_card)  # other attributes

            X2_oracle.append(card2_oracle)
            X2_card.append(card_2_card)
        except Exception as e:
            print(f"Missing or invalid data for pair ({card_1_name}, {card_2_name}): {e}")
            missing += 1
            continue

    # Convert to arrays
    X1_oracle = np.array(X1_oracle)
    X1_card = np.array(X1_card)
    X2_oracle = np.array(X2_oracle)
    X2_card = np.array(X2_card)

    if len(X1_oracle) == 0:
        print("No valid card pairs to evaluate.")
        return

    # Predict
    predictions = model.predict([X1_oracle, X1_card, X2_oracle, X2_card], verbose=0)
    pr_list = []
    # Output results
    for i in range(len(predictions)):
        pr_list.append(predictions[i][0])
        print(f"Predicted synergy of {card_pairs[i][0]} + {card_pairs[i][1]}: {predictions[i][0]:.4f}")
    print('Average Score: ', sum(pr_list)/len(pr_list))

    print(f"Evaluated {len(predictions)} pairs, {missing} skipped due to missing data.")
good_synergies = [
    ("Splinter Twin", "Deceiver Exarch"),            # Infinite combo
    ("Painter's Servant", "Grindstone"),             # Mill combo
    ("Thopter Foundry", "Sword of the Meek"),        # Token generation combo
    ("Melira, Sylvok Outcast", "Viscera Seer"),      # Persist combo (with Kitchen Finks)
    ("Kitchen Finks", "Vizier of Remedies"),         # Infinite life
    ("Heliod, Sun-Crowned", "Walking Ballista"),     # Infinite damage combo
    ("Urza, Lord High Artificer", "Winter Orb"),     # Tap for mana and lock opponent
    ("Dark Depths", "Thespian's Stage"),             # 20/20 token
    ("Yuriko, the Tiger's Shadow", "Changeling Outcast"), # Ninjutsu enabler
    ("Glistener Elf", "Scale Up"),                   # Infect kill
]

bad_synergies = [
    ("Grizzly Bears", "Time Stretch"),               # Vanilla + high-cost spell
    ("Shivan Dragon", "Relentless Rats"),            # No synergy in theme or function
    ("Opt", "Darksteel Colossus"),                   # One is cheap draw, the other is massive
    ("Pacifism", "Lightning Bolt"),                  # Redundant interaction
    ("Sakura-Tribe Elder", "Leyline of Sanctity"),   # Ramp + hand enchantment
    ("Jace, the Mind Sculptor", "Savannah Lions"),   # Aggro + control clash
    ("Doom Blade", "Phyrexian Obliterator"),         # Anti-synergy (kills your own card)
    ("Birds of Paradise", "Force of Despair"),       # Early ramp vs creature wipe
    ("Ajani's Pridemate", "Annihilating Fire"),      # Anti-synergy (removal on life-gain payoff)
    ("Goblin Piledriver", "Wall of Omens"),          # Aggro tribal vs passive draw
]
model_path = r"C:\Users\maxce\Shared Folder\Code\Maturaarbeit\data_folder\neural_network\models\adjusted_binary_small_testing_model.keras"
evaluate_synergy(model_path, good_synergies)
evaluate_synergy(model_path, bad_synergies)