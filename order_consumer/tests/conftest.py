import pytest
import os
# from pymongo import MongoClient

os.environ["DATABASE_URL"] = "postgres://db:5432"
from ..src.wsgi import app


#
#
# def test_get_db_internal():
#     client = MongoClient('mongodb://db:27017/')
#     db = client.test_database
#     return db
#
#
# @pytest.fixture(scope='module')
# def test_get_db():
#     client = MongoClient('mongodb://db:27017/')
#     db = client.test_database
#     db.users.delete_many({})
#     yield test_get_db_internal
#

@pytest.fixture(scope='module')
def test_client():
    app.testing = True
    return app.test_client()
