# encoding: utf-8
from flask import jsonify, request, g
from app import app
from store.store import Store
from protocols.export import rdf_export
from amarak.connections.alchemy import AlchemyConnection
from amarak.models import ConceptScheme
from amarak.models import DoesNotExist

store = Store()
from config import CONFIG

def get_conn():
    if not hasattr(g, 'conn'):
        g.conn = AlchemyConnection(CONFIG.get('database', 'conn_string'))
    return g.conn

SYMMETRIC = {
    u'ВЫШЕ': u'НИЖЕ',
    u'НИЖЕ': u'ВЫШЕ',
    u'ЧАСТЬ': u'ЦЕЛОЕ',
    u'ЦЕЛОЕ': u'ЧАСТЬ',
    u'АССОЦ': u'АССОЦ',
}

@app.before_request
def before_request(*args, **kwargs):
    pass
    # store.commit()

@app.after_request
def after_request(response):
    # store.commit()
    return response

def get_data():
    if request.form:
        data = request.form
    else:
        data = request.json
    return data or {}


@app.route('/schemes', methods=['GET'])
@app.route('/schemes/', methods=['GET'])
def schemes():
    conn = get_conn()
    name = request.args.get('name')
    if name:
        try:
            schemes = [conn.schemes.get(name=name)]
        except DoesNotExist:
            return jsonify({'schemes': []})
    else:
        schemes = conn.schemes.all()

    if request.args.get('offset') is not None:
        schemes = schemes.offset(request.args['offset'])

    if request.args.get('limit') is not None:
        schemes = schemes.limit(request.args['limit'])

    schemes_list = []
    for scheme in schemes:
        schemes_list.append({
            "ns_prefix": scheme.ns_prefix,
            "ns_url": scheme.ns_url,
            "name": scheme.name,
            "labels": [],
            "parents": [
                parent.name
                for parent in scheme.parents.all()
            ],
            "concept_label_types": {
                'prefLabel': 'Preferred label',
                'altLabel': 'Alternative label',
                'hiddenLabel': 'Hidden label',
            },
            "langs": {
                'ru': 'Russian',
                'en': 'English'
            }
        })
    return jsonify({'schemes': schemes_list})


@app.route('/schemes/<string:name>', methods=['PUT'])
def scheme_put(name):
    conn = get_conn()

    # ns_url = request.args.get('ns_url')
    # ns_prefix = request.args.get('ns_prefix')
    # if not ns_prefix:
    #     ns_prefix = name
    # if not ns_url:
    #     ns_url = CONFIG.get('common', 'default_namespace')

    scheme = conn.schemes.get_or_create(name=name)
    data = get_data()

    for key in ('name', 'ns_prefix', 'ns_url'):
        if key in data:
            setattr(scheme, key, data[key])

    if 'parents' in data:
        scheme.parents.clear()
        for parent_name in data['parents']:
            scheme.parents.add(conn.schemes.get(name=parent_name))

    conn.schemes.update(scheme)
    return jsonify({})


@app.route('/schemes/<string:name>', methods=['DELETE'])
def scheme_delete(name):
    conn = get_conn()
    scheme = conn.schemes.get(name=name)
    conn.schemes.delete(scheme)
    return jsonify({})


@app.route('/schemes/<string:scheme_name>/concepts/', methods=['GET'])
def scheme_concepts(scheme_name):
    conn = get_conn()
    scheme = conn.schemes.get(name=scheme_name)
    concepts = conn.concepts.filter(scheme=scheme)
    return jsonify({
        'concepts': [
            concept.to_python()
            for concept in concepts
        ]
    })
    #return jsonify({'concepts': store.top_concepts(prefix)})


@app.route('/schemes/<string:scheme_name>/concepts/top', methods=['GET'])
def scheme_top_concepts(scheme_name):
    conn = get_conn()
    scheme = conn.schemes.get(name=scheme_name)
    concepts = conn.concepts.filter(scheme=scheme)
    return jsonify({
        'concepts': [
            concept.to_python()
            for concept in concepts
        ]
    })
    #return jsonify({'concepts': store.top_concepts(prefix)})


@app.route('/schemes/<string:prefix>/parent/<string:parent>', methods=['PUT'])
def scheme_add_parent(prefix, parent):
    store.scheme_add_parent(prefix, parent)
    return jsonify({})


@app.route('/schemes/<string:prefix>/parent/<string:parent_prefix>', methods=['DELETE'])
def scheme_rm_parent(prefix, parent_prefix):
    store.scheme_rm_parent(prefix, parent_prefix)
    return jsonify({})


@app.route('/schemes/<string:scheme_name>/concepts/<string:concept_name>', methods=['DELETE'])
def scheme_concept_delete(scheme_name, concept_name):
    conn = get_conn()
    scheme = conn.schemes.get(name=scheme_name)
    concept = conn.concepts.get(name=concept_name, scheme=scheme)
    conn.concepts.delete(concept)
    return jsonify({})


@app.route('/schemes/<string:scheme_name>/concepts/<string:concept_name>', methods=['PUT'])
def scheme_concept_put(scheme_name, concept_name):

    conn = get_conn()
    scheme = conn.schemes.get(name=scheme_name)
    concept = conn.concepts.get_or_create(name=concept_name, scheme=scheme)

    data = get_data()
    for key in ('name', ):
        if key in data:
            setattr(concept, key, data[key])

    if 'labels' in data:
        concept.labels.clear()
        for label_d in data['labels']:
            concept.labels.add(label_d['lang'], label_d['type'], label_d['literal'])

    conn.concepts.update(concept)
    return jsonify({})


@app.route('/schemes/<string:scheme_name>/concepts/<string:concept_name>', methods=['GET'])
def scheme_concept(scheme_name, concept_name):
    conn = get_conn()
    scheme = conn.schemes.get(name=scheme_name)
    concept = conn.concepts.get(name=concept_name, scheme=scheme)

    return jsonify({
        'name': concept.name,
        'relations': [],
        'labels': concept.labels.to_python()
    })

    # return jsonify({
    #     'name': concept,
    #     'relations': store.concept_relations(scheme, concept),
    #     'labels': store.concept_labels(
    #         scheme,
    #         concept,
    #         flat=request.args.get('flat_labels', 'true').lower()=='true'
    #     )
    # })


@app.route('/schemes/<string:scheme_name>/concepts/<string:concept_name>/label/<string:lang>/<string:label_type>/<string:label>', methods=['PUT'])
def scheme_concept_label(scheme_name, concept_name, lang, label_type, label):
    conn = get_conn()
    scheme = conn.schemes.get(name=scheme_name)
    concept = conn.concepts.get_or_create(name=concept_name, scheme=scheme)
    concept.labels.add(lang, label_type, label)
    conn.concepts.update(concept)
    # store.add_concept_label(scheme, concept, lang, type, label)
    return jsonify({})


@app.route('/schemes/<string:scheme>/concepts/<string:concept>/label/<string:lang>/<string:type>/<string:label>', methods=['DELETE'])
def rm_scheme_concept_label(scheme, concept, lang, type, label):
    store.rm_concept_label(scheme, concept, lang, type, label)
    return jsonify({})



@app.route('/schemes/<string:scheme>'
           '/add/relation/<string:relscheme>/<string:relname>'
           '/concept1/<string:scheme1>/<string:concept1>'
           '/concept2/<string:scheme2>/<string:concept2>', methods=['PUT'])
def scheme_add_relation(scheme, relscheme, relname,
                        scheme1, concept1, scheme2, concept2):
    store.concept_add_link(scheme, relscheme, relname,
                           scheme1, concept1, scheme2, concept2)
    for r1, r2 in SYMMETRIC.items():
        if relname == r1:
            store.concept_add_link(scheme, relscheme, r2,
                                   scheme2, concept2, scheme1, concept1)

    return jsonify({})

@app.route('/schemes/<string:scheme>'
           '/link/<string:relscheme>/<string:relname>'
           '/concept1/<string:scheme1>/<string:concept1>'
           '/concept2/<string:scheme2>/<string:concept2>', methods=['DELETE'])
def rm_scheme_rm_link2(scheme, relscheme, relname, scheme1, concept1, scheme2, concept2):
    store.concept_rm_link(scheme, relscheme, relname,
                           scheme1, concept1, scheme2, concept2)
    for r1, r2 in SYMMETRIC.items():
        if relname == r1:
            store.concept_rm_link(scheme, relscheme, r2,
                                  scheme2, concept2, scheme1, concept1)

    # store.rm_link(link_id)
    return jsonify({})

@app.route('/link/<string:link_id>', methods=['DELETE'])
def rm_scheme_rm_link(link_id):
    store.rm_link(link_id)
    return jsonify({})


@app.route('/search/<string:label>', methods=['GET'])
def search(label):
    concepts = store.search_by_label(label)
    return jsonify({
        'concepts': concepts
    })

@app.route('/schemes/<string:scheme>/search/name/<string:name>', methods=['GET'])
def search_by_name(scheme, name):
    concepts = store.search_by_name(scheme, name, request.args.get('limit'))
    return jsonify({
        'concepts': concepts
    })

@app.route('/export/<string:scheme>/<string:file_format>', methods=['GET'])
def export(scheme, file_format):
    return rdf_export(scheme, file_format.lower())

# @app.route('/import/skos/<string:file_format>', methods=['GET'])
# def export(scheme, file_format):
#     importer = SkosImporter('http://127.0.0.1:8000/')
#     importer.do_import(path, "turtle")
#     return ''
