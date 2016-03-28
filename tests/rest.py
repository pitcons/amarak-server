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

    def test_schemes(self):
        scheme1 = ConceptScheme('example1', ('example1', 'http://example1.com'))
        scheme2 = ConceptScheme('example2', ('example2', 'http://example2.com'))
        self.conn.schemes.update(scheme1)
        self.conn.schemes.update(scheme2)
        rv = self.app.get('/schemes/')
        self.assertEquals(
            json.loads(rv.data),
            {
                'schemes': [
                    {
                        u'name': u'example1',
                        u'labels': [],
                        u'ns_prefix': u'example1',
                        u'ns_url': u'http://example1.com',
                        u'parents': [],
                        u'concept_label_types': {
                            u'altLabel': u'Alternative label',
                            u'hiddenLabel': u'Hidden label',
                            u'prefLabel': u'Preferred label'
                        },
                        u'langs': {
                            u'ru': u'Russian',
                            u'en': u'English'
                        }
                    },
                    {
                        u'name': u'example2',
                        u'labels': [],
                        u'ns_prefix': u'example2',
                        u'ns_url': u'http://example2.com',
                        u'parents': [],
                        u'concept_label_types': {
                            u'altLabel': u'Alternative label',
                            u'hiddenLabel': u'Hidden label',
                            u'prefLabel': u'Preferred label'
                        },
                        u'langs': {
                            u'ru': u'Russian',
                            u'en': u'English'
                        }
                    },
                ]
            }
        )

    def test_new_scheme(self):
        self.app.put('/schemes/new-scheme')
        scheme = self.conn.schemes.all()[0]
        self.assertEquals(scheme.name, 'new-scheme')

    def test_update_scheme(self):
        self.app.put('/schemes/new-scheme')
        self.app.put('/schemes/new-scheme', data={
            'name': 'new-name'
        })

        schemes = list(self.conn.schemes.all())
        self.assertEquals(len(schemes), 1)
        self.assertEquals(schemes[0].name, 'new-name')

    def test_delete_scheme(self):
        self.app.put('/schemes/new-scheme')
        self.app.delete('/schemes/new-scheme')

        schemes = list(self.conn.schemes.all())
        self.assertEquals(len(schemes), 0)


class RestConceptsTestCase(TestDB):

    def setUp(self):
        super(RestConceptsTestCase, self).setUp()
        # self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()

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
        scheme = ConceptScheme('example', ('example', 'http://example.com'))
        self.conn.update(scheme)
        concept = Concept('concept', scheme=scheme)
        self.conn.update(concept)

        self.app.put('/schemes/example/concepts/concept/label/en/altLabel/some-label-1')
        self.app.put('/schemes/example/concepts/concept/label/en/altLabel/some-label-2')
        self.app.put('/schemes/example/concepts/concept/label/ru/altLabel/some-label-3')

        concept = self.conn.concepts.filter(scheme=scheme)[0]
        self.assertEquals(
            concept.labels.all(),
            [Label("en", "altLabel", "some-label-1"),
             Label("en", "altLabel", "some-label-2"),
             Label("ru", "altLabel", "some-label-3")]
        )


    def test_get_labels(self):
        scheme = ConceptScheme('example', ('example', 'http://example.com'))
        self.conn.update(scheme)
        concept = Concept('concept', scheme=scheme)
        self.conn.update(concept)

        self.app.put('/schemes/example/concepts/concept/label/en/altLabel/some-label-1')
        self.app.put('/schemes/example/concepts/concept/label/en/altLabel/some-label-2')
        self.app.put('/schemes/example/concepts/concept/label/ru/altLabel/some-label-3')

        self.assertEquals(
            json.loads(self.app.get('/schemes/example/concepts/concept').data)['labels'],
            [{u'lang': u'en', u'literal': u'some-label-1', u'type': u'altLabel'},
             {u'lang': u'en', u'literal': u'some-label-2', u'type': u'altLabel'},
             {u'lang': u'ru', u'literal': u'some-label-3', u'type': u'altLabel'}]
        )


if __name__ == '__main__':
    unittest.main()
