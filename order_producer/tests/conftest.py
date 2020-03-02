import pytest
import os
import app

os.environ["DATABASE_URL"] = "postgres://db:5432"


@pytest.fixture(scope='module')
def test_client():
    app.testing = True
    return app.test_client()


@pytest.fixture
def kafka_producer(kafka_producer_factory):
    """Return a KafkaProducer fixture"""
    yield kafka_producer_factory()


@pytest.fixture
def kafka_producer_factory(kafka_broker, request):
    """Return a KafkaProduce factory fixture"""
    _producer = [None]

    def factory(**kafka_producer_params):
        params = {} if kafka_producer_params is None else kafka_producer_params.copy()
        params.setdefault('client_id', 'producer_%s' % (request.node.name,))
        _producer[0] = next(kafka_broker.get_producers(cnt=1, **params))
        return _producer[0]

    yield factory

    if _producer[0]:
        _producer[0].close()
