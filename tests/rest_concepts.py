# coding: utf-8
import json

from app import app
import unittest
import tempfile
from protocols.rest import *

import sqlalchemy
from amarak import Concept, ConceptScheme, Label
from .base import TestDB


class RestConceptsTestCase(TestDB):

    def setUp(self):
        super(RestConceptsTestCase, self).setUp()
        # self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()

    def _create_labels(self):
        scheme = ConceptScheme('example', ('example', 'http://example.com'))
        self.conn.update(scheme)
        concept = Concept('concept', scheme=scheme)
        self.conn.update(concept)

        self.app.put('/schemes/example/concepts/concept/labels/', data={
            'lang': 'en',
            'type': 'altLabel',
            'literal': 'some-label-1'
        })
        self.app.put('/schemes/example/concepts/concept/labels/', data={
            'lang': 'en',
            'type': 'altLabel',
            'literal': 'some-label-2'
        })
        self.app.put('/schemes/example/concepts/concept/labels/', data={
            'lang': 'ru',
            'type': 'altLabel',
            'literal': 'some-label-3'
        })

        return scheme, concept

    def test_new_concept(self):
        scheme = ConceptScheme('example', ('example', 'http://example.com'))
        self.conn.schemes.update(scheme)
        response = self.app.put('/schemes/example/concepts/new-concept')

        concepts = list(self.conn.concepts.filter(scheme=scheme))
        self.assertEquals(len(concepts), 1)
        self.assertEquals(concepts[0].name, 'new-concept')
        self.assertEquals(concepts[0].scheme.name, 'example')

    def test_update_concept(self):
        scheme = ConceptScheme('example', ('example', 'http://example.com'))
        self.conn.schemes.update(scheme)
        self.app.put('/schemes/example/concepts/new-concept')

        self.app.put('/schemes/example/concepts/new-concept', data={
            'name': 'new-name'
        })

        concepts = list(self.conn.concepts.filter(scheme=scheme))
        self.assertEquals(len(concepts), 1)
        self.assertEquals(concepts[0].name, 'new-name')

    def test_delete_concept(self):
        scheme = ConceptScheme('example', ('example', 'http://example.com'))
        self.conn.schemes.update(scheme)
        self.app.put('/schemes/example/concepts/new-concept')
        concepts = list(self.conn.concepts.filter(scheme=scheme))
        self.assertEquals(len(concepts), 1)

        self.app.delete('/schemes/example/concepts/new-concept')
        concepts = list(self.conn.concepts.filter(scheme=scheme))
        self.assertEquals(len(concepts), 0)

    def test_new_label(self):
        scheme, concept = self._create_labels()

        concept = self.conn.concepts.filter(scheme=scheme)[0]
        self.assertEquals(
            concept.labels.all(),
            [Label("en", "altLabel", "some-label-1", id=1),
             Label("en", "altLabel", "some-label-2", id=2),
             Label("ru", "altLabel", "some-label-3", id=3)]
        )

    def test_get_labels(self):
        self._create_labels()

        self.assertEquals(
            json.loads(self.app.get('/schemes/example/concepts/concept').data)['labels'],
            [{u'lang': u'en', u'literal': u'some-label-1', u'type': u'altLabel', 'id': 1},
             {u'lang': u'en', u'literal': u'some-label-2', u'type': u'altLabel', 'id': 2},
             {u'lang': u'ru', u'literal': u'some-label-3', u'type': u'altLabel', 'id': 3}]
        )

    def test_delete_labels(self):
        self._create_labels()
        self.app.delete('/schemes/example/concepts/concept/labels/1')
        self.app.delete('/schemes/example/concepts/concept/labels/3')

        self.assertEquals(
            json.loads(self.app.get('/schemes/example/concepts/concept').data)['labels'],
            [{u'lang': u'en', u'literal': u'some-label-2', u'type': u'altLabel', 'id': 2}]
        )


if __name__ == '__main__':
    unittest.main()
