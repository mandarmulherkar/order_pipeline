from ..app import produce_orders
import pytest


def test_file_size():
    with pytest.raises(Exception):
        # no Producer
        assert produce_orders('data/orders-subset-one.json', None)


def test_bad_file():
    with pytest.raises(Exception):
        # Bad JSON file
        assert produce_orders('data/orders-subset-one-bad.json', None)
