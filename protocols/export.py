# encoding: utf-8
import sys
import urllib
import logging
from urllib import urlencode, quote
from rdflib import Namespace
from rdflib import Graph, BNode, Literal
from rdflib.namespace import RDF, SKOS


from store import Store
from store.backends.sqlalchemy_store import *


store = Store()


def rdf_export(scheme_name, export_format):
    graph = Graph()
    graph.bind('skos', 'http://www.w3.org/2004/02/skos/core#')

    schemes = store.schemes()
    scheme = schemes[scheme_name]
    ns = Namespace(scheme['uri'])

    scheme_uid = ns['Scheme']

    graph.bind(scheme['prefix'], scheme['uri'])
    graph.add((scheme_uid, RDF.type, SKOS.ConceptScheme))

    # Scheme labels
    for lang, label in scheme['labels'].items():
        graph.add((scheme_uid, SKOS.prefLabel, Literal(label, lang=lang)))

    # Concepts
    for concept in store.concept_all(scheme['prefix']):
        graph.add((ns[concept.skos_name()], RDF.type, SKOS.Concept))
        for label in concept.labels:
            graph.add((ns[concept.skos_name()],
                       SKOS[label.type],
                       Literal(label.label, lang=lang)))
    # Links
    for link in store.link_all(scheme['prefix']):
        encoded2 = link.concept2.uri.replace(' ', '_')
        graph.add((ns[link.concept1.skos_name()],
                   ns[link.relation.name],
                   ns[link.concept2.skos_name()]))
        #graph.add()
            # print link.concept1_id
            # print link.concept2_id
    return graph.serialize(format='turtle')
