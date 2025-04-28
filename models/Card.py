import util
from util import card_util

# [Source, Path, Side-related, Save to memory, Save to collection, Version-dependent, Only frontside matters, Data type]
additional_attributes = ['number', 'set', 'language', 'finish']




class BaseCard():
    def __init__(self, index=None,search_params=None):
        if not index and search_params:
            index = card_util.get_card_index([search_params])[0]
        elif not not index:
            print('invalid card initiation')
            del self
        self.__dict__ = card_util.get
class Card(BaseCard):
    def __init__(self, args):
        for attribute in args:
            if attribute in additional_attributes:
                setattr(self, attribute, args[attribute])