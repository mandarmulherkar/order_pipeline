from flask import Flask
from redis import Redis
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
    app.run(host="0.0.0.0", debug=True)
