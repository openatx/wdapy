# coding: utf-8
#

from __future__ import annotations

import dataclasses
import json


def camel_to_snake(s: str) -> str:
    return ''.join(['_'+c.lower() if c.isupper() else c for c in s]).lstrip("_")


def omit_empty(d: list | dict | dataclasses.dataclass | None):
    if isinstance(d, list):
        return [omit_empty(v) for v in d]
    elif isinstance(d, dict):
        return {k: omit_empty(v) for k, v in d.items() if v is not None}
    elif dataclasses.is_dataclass(d):
        return omit_empty(dataclasses.asdict(d))
    else:
        return d
    

def json_dumps_omit_empty(data: dict) -> str:
    """
    Convert a dictionary to a JSON string, omitting any items with a value of None.
    
    Parameters:
    data (dict): The dictionary to convert to a JSON string.
    
    Returns:
    str: A JSON string representation of the dictionary with None values omitted.
    """
    return json.dumps(omit_empty(data))