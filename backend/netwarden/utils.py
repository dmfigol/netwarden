from collections import ChainMap
from typing import Iterable


def merge_dicts(dicts: Iterable):
    result = dict(ChainMap(dicts))
    return result
