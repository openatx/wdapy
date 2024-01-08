# coding: utf-8
#

from wdapy._utils import camel_to_snake, json_dumps_omit_empty
from wdapy._proto import *
from wdapy._types import *

def test_camel_to_snake():
    assert "this_is_my_string" == camel_to_snake("ThisIsMyString")



def test_json_dumps_omit_empty():
    # Test with a mix of None and non-None values
    data = {
        "a": 1,
        "b": None,
        "c": "test",
        "d": [1, 2, 3],
        "e": [{
            "f": 1,
            "g": None
        }]
    }
    expected_json = '{"a": 1, "c": "test", "d": [1, 2, 3], "e": [{"f": 1}]}'
    assert json_dumps_omit_empty(data) == expected_json

    data = [Gesture(
        action=GestureAction.TAP,
        options=GestureOption(
            x=100,
            y=200
        )
    )]
    expected_json = '[{"action": "tap", "options": {"x": 100, "y": 200}}]'
    assert json_dumps_omit_empty(data) == expected_json
    
    # Test with all values as None
    data_all_none = {
        "a": None,
        "b": None
    }
    expected_json_all_none = '{}'
    assert json_dumps_omit_empty(data_all_none) == expected_json_all_none

    # Test with no None values
    data_no_none = {
        "a": 1,
        "b": "test"
    }
    expected_json_no_none = '{"a": 1, "b": "test"}'
    assert json_dumps_omit_empty(data_no_none) == expected_json_no_none

    # Test with empty dictionary
    data_empty = {}
    expected_json_empty = '{}'
    assert json_dumps_omit_empty(data_empty) == expected_json_empty
