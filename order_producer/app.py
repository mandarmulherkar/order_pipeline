from flask import Flask
from redis import Redis
from kafka import KafkaProducer
from time import sleep
from random import randint
from kafka.errors import NoBrokersAvailable
import json
import os
import time

app = Flask(__name__)
redis = Redis(host='redis', port=6379)
KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL')
TRANSACTIONS_TOPIC = os.environ.get('TRANSACTIONS_TOPIC')


@app.route('/')
def hello_world():
    return 'Hello, World!'


def check_stream_available():
    global producer
    while True:
        try:
            producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER_URL,
                                     value_serializer=lambda value: json.dumps(value).encode(), )
            break
        except NoBrokersAvailable:
            print("Waiting for kafka...")


def produce_orders(filename: str):
    # Read orders from data file.
    with open(filename) as f:
        data = json.load(f)

    order_index = 0
    while True:
        try:
            order = data[order_index]
            message: str = json.dumps(order)
            producer.send(TRANSACTIONS_TOPIC, value=message)
            print(order)
            # sleep(randint(1, 2))
            order_index = order_index + 1
        except NoBrokersAvailable:
            print("Will try again")
        except IndexError:
            print("No more orders!")
            break


if __name__ == "__main__":
    # Check Kafka is available
    check_stream_available()
    # Add a time delay for the consumer to be ready.
    time.sleep(3)

    produce_orders('data/orders-subset-small.json')
