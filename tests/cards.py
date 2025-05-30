from util.database import sql_card_operations
from models.Card import BaseCard
card = BaseCard({'blue_in_color_identity':True})
print(card.salt)


