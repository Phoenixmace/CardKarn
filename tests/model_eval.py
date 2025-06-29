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
    print(sum(pr_list)/len(pr_list))

    print(f"Evaluated {len(predictions)} pairs, {missing} skipped due to missing data.")
    return pr_list
def test_model(model_path, good_list=None, bad_list=None):
    if not good_list:
        good_list = [
            # EDHREC Early Game
            ("Demonic Consultation", "Thassa's Oracle"),
            ("Exquisite Blood", "Sanguine Bond"),
            ("Tainted Pact", "Thassa's Oracle"),
            ("Dramatic Reversal", "Isochron Scepter"),
            ("Dualcaster Mage", "Twinflame"),
            ("Niv-Mizzet, Parun", "Curiosity"),
            ("Gravecrawler", "Phyrexian Altar"),
            ("Basalt Monolith", "Forsaken Monument"),
            ("Chatterfang, Squirrel General", "Pitiless Plunderer"),
            ("Bloodchief Ascension", "Mindcrank"),

            # EDHREC Late Game
            ("Aetherflux Reservoir", "Exquisite Blood"),
            ("Sheoldred, the Apocalypse", "Peer into the Abyss"),
            ("Orcish Bowmasters", "Peer into the Abyss"),
            ("Vraska, Betrayal's Sting", "Vorinclex, Monstrous Raider"),
            ("Aurelia, the Warleader", "Helm of the Host"),
            ("Teferi, Temporal Archmage", "The Chain Veil"),
            ("Approach of the Second Sun", "Mystical Tutor"),
            ("Niv-Mizzet, Visionary", "Niv-Mizzet, Parun"),
            ("Old Gnawbone", "Hellkite Charger"),
            ("Maze's End", "Reshape the Earth"),

            # Classic and Competitive Combos
            ("Splinter Twin", "Deceiver Exarch"),
            ("Painter's Servant", "Grindstone"),
            ("Thopter Foundry", "Sword of the Meek"),
            ("Melira, Sylvok Outcast", "Viscera Seer"),
            ("Kitchen Finks", "Vizier of Remedies"),
            ("Heliod, Sun-Crowned", "Walking Ballista"),
            ("Dark Depths", "Thespian's Stage"),
            ("Yuriko, the Tiger's Shadow", "Changeling Outcast"),
            ("Glistener Elf", "Scale Up"),
            ("Kiki-Jiki, Mirror Breaker", "Zealous Conscripts"),
            ("Devoted Druid", "Vizier of Remedies"),
            ("Necrotic Ooze", "Phyrexian Devourer"),
            ("Cephalid Illusionist", "Nomads en-Kor"),
            ("Reveillark", "Karmic Guide"),
            ("Sensei's Divining Top", "Counterbalance"),
            ("Rest in Peace", "Helm of Obedience"),
            ("Notion Thief", "Wheel of Fortune"),
            ("Underworld Breach", "Brain Freeze"),
            ("Tymna the Weaver", "Rograkh, Son of Rohgahh"),
        ]
    if not bad_list:
        bad_list = [
            ("Grizzly Bears", "Time Stretch"),  # Vanilla + high-cost spell
            ("Shivan Dragon", "Relentless Rats"),  # No synergy in theme or function
            ("Opt", "Darksteel Colossus"),  # One is cheap draw, the other is massive
            ("Pacifism", "Lightning Bolt"),  # Redundant interaction
            ("Sakura-Tribe Elder", "Leyline of Sanctity"),  # Ramp + hand enchantment
            ("Jace, the Mind Sculptor", "Savannah Lions"),  # Aggro + control clash
            ("Doom Blade", "Phyrexian Obliterator"),  # Anti-synergy (kills your own card)
            ("Birds of Paradise", "Force of Despair"),  # Early ramp vs creature wipe
            ("Ajani's Pridemate", "Annihilating Fire"),  # Anti-synergy (removal on life-gain payoff)
            ("Goblin Piledriver", "Wall of Omens"),  # Aggro tribal vs passive draw
        ]
    good_synergies = evaluate_synergy(model_path, good_list)
    bad_synergies = evaluate_synergy(model_path, bad_list)
    print(f"Good synergies: {sum(good_synergies)/len(good_synergies):.4f}")
    print(f"Bad synergies: {sum(bad_synergies)/len(bad_synergies):.4f}")
    print(f"Difference: {sum(good_synergies)/len(good_synergies) - sum(bad_synergies)/len(bad_synergies):.4f}")
    print(f"Average synergy: {(sum(good_synergies)+sum(bad_synergies))/len(good_synergies+bad_synergies):.4f}")
    return good_synergies, bad_synergies

model_path = r"C:\Users\maxce\Shared Folder\Code\Maturaarbeit\data_folder\neural_network\models\binary_small_testing_model.keras"
test_model(model_path)
