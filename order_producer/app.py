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


def check_stream_available():
    while True:
        try:
            producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER_URL,
                                     value_serializer=lambda value: json.dumps(value).encode(), )
            break
        except NoBrokersAvailable:
            print("Waiting for kafka...")

    return producer


def produce_orders(filename: str, order_producer: KafkaProducer):
    # Read orders from data file.
    with open(filename) as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError:
            print("Bad orders data file! Need JSON")
            return

    order_index = 0
    while True:
        try:
            order = data[order_index]
            message: str = json.dumps(order)
            try:
                order_producer.send(TRANSACTIONS_TOPIC, value=message)
            except NoBrokersAvailable:
                print("Stream not available, cannot send message.")
            print(order)
            sleep(randint(1, 2))
            order_index = order_index + 1
        except NoBrokersAvailable:
            print("Will try again")
        except IndexError:
            print("No more orders!")
            break

    return order_index


if __name__ == "__main__":
    # Check Kafka is available
    producer = check_stream_available()
    # Add a time delay for the consumer to be ready.
    time.sleep(3)

    produce_orders('data/orders.json', producer)
