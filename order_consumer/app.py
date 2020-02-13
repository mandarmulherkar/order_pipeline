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

    def __init__(self, name, service, ordered_at, status=CssConstants.ORDER_RECEIVED):
        self.name = name
        self.service = service
        self.ordered_at = ordered_at
        self.status = status

    def __repr__(self):
        return '<id {}>'.format(self.id)


class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String())
    result_all = db.Column(JSON)
    result_no_stop_words = db.Column(JSON)

    def __init__(self, url, result_all, result_no_stop_words):
        self.url = url
        self.result_all = result_all
        self.result_no_stop_words = result_no_stop_words

    def __repr__(self):
        return '<id {}>'.format(self.id)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, email):
        self.email = email


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
            print("Trying to read kafka...")

    app.run(host="0.0.0.0", debug=True)
