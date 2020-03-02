from ..app import produce_orders
from ..app import wait_to_send_message
from datetime import datetime
import pytest


def test_file_size():
    with pytest.raises(Exception):
        # No Producer
        assert produce_orders('data/orders-subset-one.json', None)


def test_bad_file():
    with pytest.raises(Exception):
        # Bad JSON file
        assert produce_orders('data/orders-subset-one-bad.json', None)


def test_time_between_orders_1():
    order = {"ordered_at": "2019-02-18T16:01:00"}
    sleep_time, current_time = wait_to_send_message(order, datetime.utcnow())
    assert sleep_time == 0
    assert current_time == datetime(2019, 2, 18, 16, 1)


def test_time_between_orders_2():
    order = {"ordered_at": "2019-02-18T16:01:00"}
    previous_time = datetime.utcnow().replace(year=2019, month=2, day=18, hour=16, minute=2)
    sleep_time, current_time = wait_to_send_message(order, previous_time)
    assert sleep_time == 0
    assert current_time == datetime(2019, 2, 18, 16, 1)


def test_time_between_orders_3():
    order_time = datetime.utcnow().replace(year=2019, month=2, day=18, hour=15, minute=59, microsecond=0)
    order = {"ordered_at": order_time.isoformat()}
    previous_time = datetime.utcnow().replace(year=2019, month=2, day=18, hour=15, minute=57, microsecond=0)
    sleep_time, current_time = wait_to_send_message(order, previous_time)
    assert sleep_time == 12


def test_time_between_orders_4():
    order_time = datetime.utcnow().replace(year=2019, month=2, day=18, hour=15, minute=59, microsecond=0)
    order = {"ordered_at": order_time.isoformat()}
    previous_time = datetime.utcnow().replace(year=2019, month=2, day=18, hour=15, minute=50, microsecond=0)
    sleep_time, current_time = wait_to_send_message(order, previous_time)
    assert sleep_time == 0
