#!/usr/bin/env python3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from kafka import KafkaConsumer
from redis import Redis
from sqlalchemy.dialects.postgresql import JSON
from models.css_constants import CssConstants
import os
import json
import logging
import ast
from datetime import datetime

app = Flask(__name__)
app.config.from_object("config.Config")
db = SQLAlchemy(app)

redis = Redis(host='redis', port=6379)
KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL')
TRANSACTIONS_TOPIC = os.environ.get('TRANSACTIONS_TOPIC')


class CssOrder(db.Model):
    __tablename__ = 'received_orders'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    service = db.Column(db.String())
    status = db.Column(db.String())
    ordered_at = db.Column(db.Date())
    created_at = db.Column(db.Date(), default=datetime.utcnow)

    def __init__(self, name, service, ordered_at, status=CssConstants.ORDER_RECEIVED):
        self.name = name
        self.service = service
        self.ordered_at = ordered_at
        self.status = status

    def __repr__(self):
        return '<id {}>'.format(self.id)


class Items(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('received_orders.id'))
    name = db.Column(db.String())
    price_per_unit = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    created_at = db.Column(db.Date(), default=datetime.utcnow)

    def __init__(self, name, price_per_unit, quantity):
        self.name = name
        self.price_per_unit = price_per_unit
        self.quantity = quantity

    def __repr__(self):
        return '<order_id: {}, id {}>'.format(self.order_id, self.id)


@app.route('/')
def hello():
    redis.incr('hits')
    return 'The Consumer has been viewed %s time(s).' % redis.get('hits')


if __name__ == "__main__":
    while True:
        try:
            consumer = KafkaConsumer(TRANSACTIONS_TOPIC, bootstrap_servers=[KAFKA_BROKER_URL],
                                     value_deserializer=json.loads)
            break
        except:
            print("Trying to connect to Kafka")

    while True:
        try:
            for message in consumer:
                order: dict = message.value
                logging.info("Received message {}".format(message))
                json_order = ast.literal_eval(message.value)
                print(json_order)
                css_order = CssOrder(json_order['name'], json_order['service'], json_order['ordered_at'])
                db.session.add(css_order)
                db.session.commit()
        except TypeError:
            print("Waiting for kafka...")

    app.run(host="0.0.0.0", debug=True)
