#!/usr/bin/env python3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from kafka import KafkaConsumer
from redis import Redis
from rq import Queue, Worker
from datetime import datetime
import psycopg2
import os
import json
import logging
import ast
from sys import modules
from os.path import basename, splitext

from job_worker import JobWorker
from wsgi import app, db
from css_order import CssOrder
from menu_item import MenuItem
from order_item import OrderItem

# def enqueueable(func):
#     if func.__module__ == "__main__":
#         func.__module__, _ = splitext(basename(modules["__main__"].__file__))
#     return func
#
#
# @enqueueable
# def process(order_id):
#     print(">>>>>>>>>>>>>>> RQ Processing item {}".format(order_id))
#

# app = Flask(__name__)
# app.config.from_object("config.Config")
# db = SQLAlchemy(app)

redis_conn = Redis(host='redis', port=6379)
# q = Queue('order_queue', connection=redis_conn, is_async=False)
q = Queue('order_queue', connection=redis_conn)

redis = Redis(host='redis', port=6379)
KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL')
TRANSACTIONS_TOPIC = os.environ.get('TRANSACTIONS_TOPIC')


# class CssConstants:
#     ORDER_RECEIVED = "order_received"


# class CssOrder(db.Model):
#     __tablename__ = 'received_order'
#
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String())
#     service = db.Column(db.String())
#     status = db.Column(db.String())
#     items_in_order = db.Column(db.Integer())
#     ordered_at = db.Column(db.DateTime())
#     created_at = db.Column(db.DateTime(), default=datetime.utcnow)
#
#     def __init__(self, name, service, items_in_order, ordered_at, status=CssConstants.ORDER_RECEIVED):
#         self.name = name
#         self.service = service
#         self.items_in_order = items_in_order
#         self.ordered_at = datetime.strptime(ordered_at, "%Y-%m-%dT%H:%M:%S")
#         self.status = status
#
#     def __repr__(self):
#         return '<id {}>'.format(self.id)


# class MenuItem(db.Model):
#     __tablename__ = 'menu_item'
#
#     id = db.Column(db.Integer, primary_key=True)
#     cook_time = db.Column(db.Integer)
#     name = db.Column(db.String())
#
#     def __init__(self, name, cook_time):
#         self.cook_time = cook_time
#         self.name = name
#
#     def __repr__(self):
#         return '<name: {}, cook_time {}>'.format(self.name, self.cook_time)


# class OrderItem(db.Model):
#     __tablename__ = 'order_item'
#
#     id = db.Column(db.Integer, primary_key=True)
#     order_id = db.Column(db.Integer, db.ForeignKey('received_order.id'))
#     name = db.Column(db.String())
#     price_per_unit = db.Column(db.Integer)
#     quantity = db.Column(db.Integer)
#     created_at = db.Column(db.DateTime(), default=datetime.utcnow)
#
#     def __init__(self, order_id, name, price_per_unit, quantity):
#         self.order_id = order_id
#         self.name = name
#         self.price_per_unit = price_per_unit
#         self.quantity = quantity
#
#     def __repr__(self):
#         return '<order_id: {}, id {}>'.format(self.order_id, self.id)


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

    db.create_all()

    return True


if __name__ == "__main__":
    print("consumer >> I am in CONSUMER")
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

        while True:
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
                    print("#############################")
                    print("## {}".format(css_order.id))
                    print("## {}".format(css_order.name))
                    print("#############################")

                    for item in json_order_items:
                        order_item = OrderItem(css_order.id, item['name'], item['price_per_unit'], item['quantity'])
                        db.session.add(order_item)
                        db.session.commit()
                        menu_item = MenuItem.query.filter_by(name=item['name']).first()

                        print("###################################")
                        job = q.enqueue(JobWorker.process_item, css_order.id, order_item.id, item['quantity'],
                                        menu_item.cook_time,
                                        menu_item.name)
                        print("## {}".format(job))
                        print("###################################")

                    print("###################################")
                    job = q.enqueue(JobWorker.process, css_order.id)
                    print("## {}".format(job))
                    print("###################################")

                    # # Worker Stats
                    # # workers = Worker.all(connection=redis)
                    # workers = Worker.all(queue=q)
                    # for worker in workers:
                    #     print("Worker {} {} {} {}".format(worker.name, worker.successful_job_count,
                    #                                       worker.failed_job_count,
                    #                                       worker.total_working_time))

            except TypeError as te:
                print("Waiting for kafka... {}".format(str(te)))

    else:
        print("Error setting up the database tables")
