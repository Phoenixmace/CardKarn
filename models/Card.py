import scrython

from util.json_util import get_data, dump_data, set_value, increment_value_by
import requests
# what if wrong set/name code
# make other lists than main first man
# card faces to class

# [Source, Path, Side-related, Save to memory, Save to collection, Version-dependent, Only frontside matters, Data type]
additional_attributes = ['number', 'set', 'language', 'finish']




class BaseCard():
    def __init__(self, data):
        self.__dict__ = data
        print()
class Card(BaseCard):
    def __init__(self, args):
        for attribute in args:
            if attribute in additional_attributes:
                setattr(self, attribute, args[attribute])