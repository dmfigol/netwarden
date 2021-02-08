from typing import Iterable, Dict, Any, Type, TypeVar

T = TypeVar("T")


def merge_dicts(*dicts: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """Merges several dictionaries into one

    Args:
        *dicts: dictionaries to merge

    Returns:
        A dictionary with keys and values from all input dictionaries.
    """
    result = {
        key: value
        for d in dicts
        for key, value in d.items()
    }
    return result


def no_op(value: T) -> T:
    return value
