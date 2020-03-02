from ..src.consumer import read_order
import json
import os

order_list = [
    {
        "items": [
            {
                "name": "Puff Pastry Chicken Potpie",
                "price_per_unit": 1250,
                "quantity": 1
            },
            {
                "name": "Blue Cheese-Crusted Sirloin Steaks",
                "price_per_unit": 1000,
                "quantity": 1
            },
            {
                "name": "The Ultimate Chicken Noodle Soup",
                "price_per_unit": 1150,
                "quantity": 1
            }
        ],
        "name": "Monica Martin",
        "service": "ClubNub",
        "ordered_at": "2019-02-18T16:01:00"
    },
]


def test_read_order_1():
    json_order = order_list[0]
    string_order = json.dumps(json_order)
    order = read_order(string_order)
    assert order['name'] == 'Monica Martin'


def test_read_order_2():
    json_order = order_list[0]
    string_order = json.dumps(json_order)
    order = read_order(string_order)
    assert len(order['items']) == 3


# These should be last, it destroys the order
def test_read_order_3():
    json_order = order_list[0]
    json_order['ordered_at'] = "2019-02-18T16:01:"
    string_order = json.dumps(json_order)
    order = read_order(string_order)
    assert order is None


def test_read_order_4():
    json_order = order_list[0]
    json_order['ordered_at'] = "2019-02-18T16:01:"
    string_order = json.dumps(json_order)
    order = read_order(string_order)
    assert order is None


def test_read_order_5():
    json_order = order_list[0]
    json_order['ordered_at'] = "2019-02-18T16:01:00"
    json_order['items'] = []
    string_order = json.dumps(json_order)
    order = read_order(string_order)
    assert order is None


def test_read_order_6():
    json_order = order_list[0]
    json_order['ordered_at'] = "2019-02-18T16:01:00"
    del json_order['items']
    string_order = json.dumps(json_order)
    order = read_order(string_order)
    assert order is None
