import pytest

from netwarden import utils


@pytest.mark.parametrize(
    "input_dicts,output_dict",
    [([{"a": 1, "b": 2}, {"b": 3, "c": 4}], {"a": 1, "b": 3, "c": 4})],
)
def test_merge_dicts(input_dicts, output_dict):
    utils.merge_dicts(*input_dicts) == output_dict
