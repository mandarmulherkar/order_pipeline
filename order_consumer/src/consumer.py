#!/usr/bin/env python3
from kafka import KafkaConsumer
from redis import Redis
from rq import Queue, Worker
import psycopg2
import os
import json
import logging
import ast
import threading

from job_worker import JobWorker
from wsgi import app, db
from css_order import CssOrder
from menu_item import MenuItem
from order_item import OrderItem

redis_conn = Redis(host='redis', port=6379)
# is_async=False
q = Queue('order_queue', connection=redis_conn)

redis = Redis(host='redis', port=6379)
# Do not want workers to pick up old jobs, since these have id arguments.
redis.flushall()
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

    db.drop_all()
    db.create_all()

    return True


def start_new_thread(function):
    def decorator(*args, **kwargs):
        t = threading.Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()

    return decorator


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
            print("Trying to read messages")
            for message in consumer:
                order: dict = message.value
                logging.info("Received message {}".format(message))
                json_order = ast.literal_eval(message.value)
                print(json_order)
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
