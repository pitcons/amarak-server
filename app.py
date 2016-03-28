# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.babel import Babel


app = Flask(__name__)
babel = Babel(app)

@app.teardown_request
def teardown_request(exception):
    from store.backends.sqlalchemy_store import session
    if exception:
        session.rollback()
        session.remove()
    session.remove()


@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response
