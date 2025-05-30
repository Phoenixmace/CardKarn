from util.database import sql_card_operations
from models.Card import BaseCard
card = BaseCard({'name':'thassas oracle'})
print(card.salt)


