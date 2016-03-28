# coding: utf-8
import unittest
import difflib
import json
from os.path import join
import sqlalchemy
from sqlalchemy_utils import (database_exists,
                              create_database,
                              drop_database)
from config import CONFIG
CONFIG.set('common', 'is_testing', 'True')
CONFIG.set('database', 'conn_string', CONFIG.get('database', 'test_conn_string'))
from amarak.connections.alchemy.tables import Base
from amarak.connections.alchemy import AlchemyConnection
from amarak.connections.rest import RestConnection
from protocols.rest import *



class TestRestConnection(RestConnection):

    def __init__(self, client):
        super(TestRestConnection, self).__init__(self)
        self.url = '/'
        self.client = client

    def _loads_or_show(self, url, data, response):
        try:
            return json.loads(response)
        except ValueError:
            raise ValueError([url, data, response])

    def _get(self, url, data=None):
        url = join(self.url, url)
        response = self.client.get(url, query_string=data)

        return self._loads_or_show(url, data, response.data)

    def _put(self, url, data=None, as_json=True):
        url = join(self.url, url)
        if as_json:
            headers = [('Content-Type', 'application/json')]
            json_data = json.dumps(data)
            json_data_length = len(json_data)
            headers.append(('Content-Length', json_data_length))
            response = self.client.put(url, data=json_data, headers=headers)
        else:
            raise NotImplementedError
            # response = self.client.put(url, data)

        return self._loads_or_show(url, data, response.data)


class TestDB(unittest.TestCase):

    def setUp(self):
        self.engine = sqlalchemy.create_engine(
            CONFIG.get('database', 'test_conn_string'),
            isolation_level="AUTOCOMMIT"
        )
        if not database_exists(self.engine.url):
            create_database(self.engine.url)

        self.maxDiff = None
        self.connection = self.engine.connect()
        Base.metadata.create_all(self.engine, checkfirst=True)
        self.conn = AlchemyConnection(self.engine.url)

    def tearDown(self):
        drop_database(self.engine.url)

    # def assertMultiLineEqual(self, first, second, msg=None):
    #     """Assert that two multi-line strings are equal.

    #     If they aren't, show a nice diff.

    #     """
    #     self.assertTrue(isinstance(first, str),
    #                     'First argument is not a string')
    #     self.assertTrue(isinstance(second, str),
    #                     'Second argument is not a string')

    #     if first != second:
    #         message = ''.join(difflib.ndiff(first.splitlines(True),
    #                                         second.splitlines(True)))
    #         if msg:
    #             message += " : " + msg

    #         self.fail("Multi-line strings are unequal:\n" + message)
