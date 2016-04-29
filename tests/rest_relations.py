# coding: utf-8
import json

from app import app
import unittest
import tempfile
from protocols.rest import *

import sqlalchemy
from amarak import Concept, ConceptScheme, Label
from .base import TestDB


class RestRelationsTestCase(TestDB):

    def setUp(self):
        super(RestRelationsTestCase, self).setUp()
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        super(RestRelationsTestCase, self).tearDown()

    def test_relations(self):
        scheme = ConceptScheme('example1', ('example1', 'http://example1.com'))
        self.conn.schemes.update(scheme)

        self.app.put('/schemes/example1/relations/new-rel')

        relations = list(self.conn.schemes.all())
        self.assertEquals(
            relations[0].relations.all()[0],
            Relation(scheme, 'new-rel')
        )

    def test_delete_relation(self):
        scheme = ConceptScheme('example1', ('example1', 'http://example1.com'))
        self.conn.schemes.update(scheme)

        self.app.put('/schemes/example1/relations/new-rel')
        self.app.delete('/schemes/example1/relations/new-rel')

        relations = list(self.conn.schemes.all())[0].relations.all()
        self.assertEquals(len(relations), 0)

    def test_update_relations(self):
        scheme = ConceptScheme('example1', ('example1', 'http://example1.com'))
        self.conn.schemes.update(scheme)

        self.app.put('/schemes/example1/relations/new-rel')
        self.app.put('/schemes/example1/relations/new-rel', data={
            'name': 'new-rel-new-name'
        })

        relations = list(self.conn.schemes.all())
        self.assertEquals(len(relations), 1)
        self.assertEquals(
            relations[0].relations.all()[0],
            Relation(scheme, 'new-rel-new-name')
        )
