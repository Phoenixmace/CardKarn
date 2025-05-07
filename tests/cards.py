from models import Card

card = Card.BaseCard(search_params={'name':'Demonic Tutor'})
card_1 = Card.BaseCard(search_params={'name':'gaias vengeance'})
card_2 = Card.BaseCard(search_params={'id':'0000419b-0bba-4488-8f7a-6194544ce91e'})
print(card_2.__dict__)
print(card.__dict__)
print(card_1.__dict__)
card.store_base_card_dict()
