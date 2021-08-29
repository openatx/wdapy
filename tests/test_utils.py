# coding: utf-8
#

from wdapy._utils import camel_to_snake


def test_camel_to_snake():
    assert "this_is_my_string" == camel_to_snake("ThisIsMyString")
