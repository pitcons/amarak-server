# coding: utf-8

import os
import json
from StringIO import StringIO
from pprint import pprint
from app import app
import unittest
from .base import TestDB, TestRestConnection
from amarak.importers.importer_skos import SkosImporter
from amarak.connections.rest import RestConnection
from amarak import Concept, ConceptScheme, Label

PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'export_samples')


class ImportTestCase(TestDB):

    def setUp(self):
        super(ImportTestCase, self).setUp()
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_skos(self):
        conn = TestRestConnection(self.app)
        importer = SkosImporter(conn)
        importer.do_import(os.path.join(PATH, 'simple1.ttl'), "turtle")

        schemes = list(self.conn.schemes.all())
        self.assertEquals(len(schemes), 1)

        scheme = schemes[0]
        self.assertEquals(scheme.name, 'example1')
        self.assertEquals(scheme.ns_prefix, 'example1')
        self.assertEquals(scheme.ns_url, 'http://example1.com/')

        concepts = list(self.conn.concepts.filter(scheme=scheme))
        self.assertEquals(len(concepts), 2)


        self.assertEquals(concepts[0].name, 'Concept1')
        self.assertEquals(
            concepts[0].labels.all(),
            [Label("en", "altLabel", "Concept(Alternative) 1"),
             Label("en", "hiddenLabel", "Concept(Hidden) 1"),
             Label("en", "prefLabel", "Concept 1"),
             Label("en", "prefLabel", "Concept(Second) 1"),
             Label("ru", "altLabel", "Концепт(Альтернативно) 1"),
             Label("ru", "hiddenLabel", "Концепт(Скрыто) 1"),
             Label("ru", "prefLabel", "Концепт 1")]
        )

        self.assertEquals(concepts[1].name, 'Concept2')
        self.assertEquals(
            concepts[1].labels.all(),
            []
        )
