from flask import Flask
from redis import Redis
from kafka import KafkaProducer
from time import sleep
from kafka.errors import NoBrokersAvailable
import json
import os
from datetime import datetime
import logging
import time

app = Flask(__name__)
redis = Redis(host='redis', port=6379)
KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL')
TRANSACTIONS_TOPIC = os.environ.get('TRANSACTIONS_TOPIC')

TIME_SPEED = 10
ORDER_FILE_NAME = 'data/orders.json'


def check_stream_available():
    """
    Check that the kafka stream is available before sending orders.
    :return:
    """
    while True:
        try:
            producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER_URL,
                                     value_serializer=lambda value: json.dumps(value).encode(), )
            break
        except NoBrokersAvailable:
            print("Waiting for kafka...")

    return producer


def produce_orders(filename: str, order_producer: KafkaProducer):
    """
    Send orders to the kafka stream.
    :param filename: Use the filename to read orders.
    :param order_producer: The Kafka order producer
    :return: The index of the last order.
    """
    # Read orders from data file.
    with open(filename) as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError:
            print("Bad orders data file! Need JSON")
            return

    previous_time = datetime.utcnow()
    order_index = 0
    # To continue waiting for kafka if unavailable, use while True
    while True:
        try:
            order = data[order_index]
            try:
                sleep_time, current_time = wait_to_send_message(order, previous_time)
                message: str = json.dumps(order)
                logging.info(message)
            except:
                logging.error("Bad order data!")
                order_index = order_index + 1
                continue

            try:
                order_producer.send(TRANSACTIONS_TOPIC, value=message)
            except NoBrokersAvailable:
                print("Stream not available, cannot send message.")

            previous_time = current_time
            order_index = order_index + 1
        except NoBrokersAvailable:
            print("Stream not available, will try again")
        except IndexError:
            print("No more orders!")
            break

    return order_index


def wait_to_send_message(order, previous_time):
    """
    Simulate the order time, sped up with a TIME_SPEED factor.
    If the time difference is large, send order data immediately.
    :param order: The order to send
    :param previous_time: The order time from the previous order. Wait t / TIME_SPEED to send this order.
    :return: The time the producer sleeps, and the current order time, adjusted for bad data.
    """
    sleep_time = 0
    current_time = datetime.utcnow()
    try:
        created_at_current = order['ordered_at']
        current_time = datetime.strptime(created_at_current, "%Y-%m-%dT%H:%M:%S")
        logging.info(previous_time)
        time_diff = current_time - previous_time
        logging.info(time_diff)
        total_seconds = time_diff.days * 24 * 3600 + time_diff.seconds
        if 0 < total_seconds < 300:
            sleep_time = total_seconds / TIME_SPEED
            print("Sleeping for {}".format(sleep_time))
            sleep(sleep_time)
        else:
            print("Immediately sending out of order request!")
    except:
        logging.error("Something went wrong, not sleeping")
    return sleep_time, current_time


if __name__ == "__main__":
    # Check Kafka is available
    producer = check_stream_available()

    # Add a time delay for the consumer to be ready.
    time.sleep(3)

    produce_orders(ORDER_FILE_NAME, producer)
