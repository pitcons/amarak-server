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
                        u'id': u'example1',
                        u'name': u'example1',
                        u'labels': [],
                        u'ns_prefix': u'example1',
                        u'ns_url': u'http://example1.com',
                        u'parents': [],
                        u'relations': [],
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
                        u'id': u'example2',
                        u'name': u'example2',
                        u'labels': [],
                        u'ns_prefix': u'example2',
                        u'ns_url': u'http://example2.com',
                        u'parents': [],
                        u'relations': [],
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




if __name__ == '__main__':
    unittest.main()
