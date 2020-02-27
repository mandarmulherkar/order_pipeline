from flask import Flask
from redis import Redis
from kafka import KafkaProducer
from time import sleep
from random import randint
from kafka.errors import NoBrokersAvailable
import json
import os

app = Flask(__name__)
redis = Redis(host='redis', port=6379)
KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL')
TRANSACTIONS_TOPIC = os.environ.get('TRANSACTIONS_TOPIC')


@app.route('/')
def hello():
    redis.incr('hits')
    return 'The Producer has been viewed %s time(s).' % redis.get('hits')


if __name__ == "__main__":
    # Read orders from data file.
    with open('data/orders.json') as f:
        data = json.load(f)

    while True:
        try:
            producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER_URL,
                                     value_serializer=lambda value: json.dumps(value).encode(),
                                     )
            break
        except NoBrokersAvailable:
            print("Waiting for kafka...")

    i = 0
    while True:
        try:
            order = data[i]
            message: str = json.dumps(order)
            producer.send(TRANSACTIONS_TOPIC, value=message)
            print(order)
            sleep(randint(1, 2))
            i = i + 1
        except NoBrokersAvailable:
            print("Will try again")
        except IndexError:
            print("No more orders!")
            break

# app.run(host="0.0.0.0", debug=True)
