from models import Card

card = Card.BaseCard(search_params={'name':'Demonic Tutor'})
card_1 = Card.BaseCard(search_params={'name':'gaias vengeance'})
card_2 = Card.BaseCard(search_params={'name':'Demonic Tutor'})
card_1.set_array()
print(card_1.np_arrays)
card.store_base_card_dict()
