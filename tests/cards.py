from util.database import sql_card_operations
from models.Card import BaseCard
card = BaseCard({'name': 'Etali, Primal Conqueror'}, wait_for_salt_score=True)
print(card.get_np_array())


