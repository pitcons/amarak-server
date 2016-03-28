# coding: utf-8
import os
import json
from StringIO import StringIO
from app import app
import unittest
from .base import TestDB, TestRestConnection
from amarak.exporters.rdf import RdfExporter
from amarak.connections.rest import RestConnection
from amarak import Concept, ConceptScheme, Label

PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'export_samples')


class ExportTestCase(TestDB):

    def setUp(self):
        super(ExportTestCase, self).setUp()
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_export(self):
        scheme1 = ConceptScheme('example1', ('example1', 'http://example1.com/'))
        scheme2 = ConceptScheme('example2', ('example2', 'http://example2.com/'))

        self.conn.schemes.update(scheme1)
        self.conn.schemes.update(scheme2)

        concept1 = Concept('Concept1', scheme=scheme1)
        concept1.labels.add('ru', 'prefLabel', 'Концепт 1')
        concept1.labels.add('en', 'prefLabel', 'Concept 1')
        concept1.labels.add('en', 'prefLabel', 'Concept(second) 1')
        concept1.labels.add('ru', 'altLabel', 'Концепт(альтернативно) 1')
        concept1.labels.add('en', 'altLabel', 'Concept(alternative) 1')
        concept1.labels.add('ru', 'hiddenLabel', 'Концепт(скрыто) 1')
        concept1.labels.add('en', 'hiddenLabel', 'Concept(hidden) 1')
        self.conn.update(concept1)

        concept2 = Concept('Concept2', scheme=scheme1)
        self.conn.update(concept2)


        conn = TestRestConnection(self.app)
        exporter = RdfExporter(conn)

        output = StringIO()
        exporter.do_export('example1', output)

        self.assertMultiLineEqual(
            output.getvalue(),
            open(os.path.join(PATH, 'simple1.ttl')).read()
        )
