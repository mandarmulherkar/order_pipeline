#!/usr/bin/env python3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'postgres'
    try:
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    except KeyError:
        os.environ["DATABASE_URL"] = 'postgresql://postgres:postgres@db:5432/orders'
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


app = Flask(__name__)
try:
    app.config.from_object("config.Config")
except:
    logging.error("Could not import Config!")

db = SQLAlchemy(app)

if __name__ == "__main__":
    print("Starting in wsgi")
