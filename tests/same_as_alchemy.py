# coding: utf-8
from amarak.tests.alchemy_tests import SchemesTest, ConceptsTest
from base import TestDB, TestRestConnection
from app import app


class SameSchemesTest(SchemesTest, TestDB):

    def setUp(self):
        super(SameSchemesTest, self).setUp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.conn = TestRestConnection(self.app)


class SameConceptsTest(ConceptsTest, TestDB):

    def setUp(self):
        super(SameConceptsTest, self).setUp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.conn = TestRestConnection(self.app)


if __name__ == '__main__':
    unittest.main()
