#!/usr/bin/env python3
from kafka import KafkaConsumer
from redis import Redis
from rq import Queue, Worker
# Need pip install psycopg2-binary
import psycopg2
import os
import json
import ast
import threading
from datetime import datetime

import sys

if hasattr(sys, '_called_from_test'):
    from .job_worker import JobWorker
    from .wsgi import app, db
    from .css_order import CssOrder
    from .menu_item import MenuItem
    from .order_item import OrderItem

    print("Not initializing redis for pytest")
else:
    from job_worker import JobWorker
    from wsgi import app, db
    from css_order import CssOrder
    from menu_item import MenuItem
    from order_item import OrderItem

    redis_conn = Redis(host='redis', port=6379)
    q = Queue('order_queue', connection=redis_conn)

    # Do not want workers to pick up old jobs, since these have database ids as arguments.
    redis_conn.flushall()

KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL')
TRANSACTIONS_TOPIC = os.environ.get('TRANSACTIONS_TOPIC')


def setup_database():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(host="db",
                                port=5432,
                                database="orders", user="postgres",
                                password="postgres")

        cur = conn.cursor()

        query = """
            DROP TABLE IF EXISTS order_item CASCADE;
            DROP TABLE IF EXISTS received_order CASCADE;
            DROP TABLE IF EXISTS menu_item CASCADE;
        """
        print(query)
        cur.execute(query)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return False
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

    # In case of exceptions, use the sqlalchmey api.
    db.drop_all()
    db.create_all()

    return True


def start_new_thread(function):
    def decorator(*args, **kwargs):
        t = threading.Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()

    return decorator


def read_order(order):
    """
    Read the order and verify it can be parsed.
    :param order: The order dictionary from kafka.
    :return: The order in json format.
    """
    current_order = ast.literal_eval(order)
    # Validate
    try:
        current_order['name']
        current_order['ordered_at']
        current_order['items']
        current_order['service']
        try:
            ordered_at = datetime.strptime(current_order['ordered_at'], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            try:
                ordered_at = datetime.strptime(current_order['ordered_at'], "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError:
                return None
        assert len(current_order['items']) > 0
    except (KeyError, AssertionError):
        return None

    return current_order


if __name__ == "__main__":
    print("Starting consumer...")
    if setup_database():

        # First, set up the menu items.
        with open('src/data/items.json') as f:
            menu_items = json.load(f)

        for menu_item in menu_items:
            print("Adding menu item {}".format(menu_item['name']))
            new_menu_item = MenuItem(menu_item['name'], menu_item['cook_time'])
            db.session.add(new_menu_item)
            db.session.commit()

        while True:
            try:
                consumer = KafkaConsumer(TRANSACTIONS_TOPIC, bootstrap_servers=[KAFKA_BROKER_URL],
                                         value_deserializer=json.loads)
                break
            except:
                print("Trying to connect to Kafka")

        try:
            print("Starting to read messages")
            for message in consumer:
                order: dict = message.value
                json_order = read_order(order)

                if not json_order:
                    continue

                # Items from the order
                json_order_items = json_order['items']
                items_in_order = 0
                for item in json_order_items:
                    items_in_order = items_in_order + int(item['quantity'])

                css_order = CssOrder(json_order['name'], json_order['service'], items_in_order,
                                     json_order['ordered_at'])
                db.session.add(css_order)
                db.session.commit()
                print("> Received Order #{} for {}".format(css_order.id, css_order.name))

                for item in json_order_items:
                    order_item = OrderItem(css_order.id, item['name'], item['price_per_unit'], item['quantity'])
                    db.session.add(order_item)
                    db.session.commit()
                    menu_item = MenuItem.query.filter_by(name=item['name']).first()

                    job = q.enqueue(JobWorker.process_item, css_order.id, order_item.id, item['quantity'],
                                    menu_item.cook_time,
                                    menu_item.name)

                job = q.enqueue(JobWorker.process, css_order.id)

        except TypeError as te:
            print("Waiting for kafka... {}".format(str(te)))

    else:
        print("Error setting up the database tables")
