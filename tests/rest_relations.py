# coding: utf-8
import json

from app import app
import unittest
import tempfile
from protocols.rest import *

import sqlalchemy
from amarak import Concept, ConceptScheme, Label
from .base import TestDB


class RestSchemesTestCase(TestDB):

    def setUp(self):
        super(RestSchemesTestCase, self).setUp()
        # self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        super(RestSchemesTestCase, self).tearDown()
        # os.close(self.db_fd)
        # os.unlink(app.config['DATABASE'])

    def test_relations(self):
        pass
