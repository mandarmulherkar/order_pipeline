#!/usr/bin/env python3
from flask import Flask
from kafka import KafkaConsumer
from redis import Redis
import os
import json
import logging

app = Flask(__name__)
redis = Redis(host='redis', port=6379)
KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL')
TRANSACTIONS_TOPIC = os.environ.get('TRANSACTIONS_TOPIC')


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
                print(order)
        except TypeError:
            print("Trying to read kafka...")

    app.run(host="0.0.0.0", debug=True)
