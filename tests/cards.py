from models import Card
a = ('a', 'b')
b = ['b', 'a']
b.sort()
b = tuple(b)
print(a == b)
card = Card.ShortCard(oracle_id='82004860-e589-4e38-8d61-8c0210e4ea39', update=True, search_params={'name': 'Demonic Tutor'})


print(card.get_array())
