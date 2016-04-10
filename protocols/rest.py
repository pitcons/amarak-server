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


@app.route('/schemes/', methods=['GET'])
def schemes():
    conn = get_conn()
    scheme_id = request.args.get('id')
    if scheme_id:
        try:
            schemes = [conn.schemes.get(id=scheme_id)]
        except DoesNotExist:
            return jsonify({'schemes': []})
    else:
        schemes = conn.schemes.all()

    name = request.args.get('name')
    if name:
        schemes = schemes.filter(name=name)

    if request.args.get('offset') is not None:
        schemes = schemes.offset(request.args['offset'])

    if request.args.get('limit') is not None:
        schemes = schemes.limit(request.args['limit'])

    schemes_list = []
    for scheme in schemes:
        schemes_list.append({
            "id": scheme.id,
            "ns_prefix": scheme.ns_prefix,
            "ns_url": scheme.ns_url,
            "name": scheme.name,
            "labels": scheme.labels.to_python(),
            "parents": [
                parent.id
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


@app.route('/schemes/<string:scheme_id>', methods=['PUT'])
def scheme_put(scheme_id):
    conn = get_conn()

    # ns_url = request.args.get('ns_url')
    # ns_prefix = request.args.get('ns_prefix')
    # if not ns_prefix:
    #     ns_prefix = name
    # if not ns_url:
    #     ns_url = CONFIG.get('common', 'default_namespace')

    scheme = conn.schemes.get_or_create(id=scheme_id)
    data = get_data()

    for key in ('id', 'name', 'ns_prefix', 'ns_url'):
        if key in data:
            setattr(scheme, key, data[key])

    if 'parents' in data:
        scheme.parents.clear()
        for parent_id in data['parents']:
            scheme.parents.add(conn.schemes.get(id=parent_id))

    if 'labels' in data:
        print data['labels']
        # TODO implement
        scheme.labels.clear()
        for label in data['labels']:
            scheme.labels.add(label['lang'], label['type'], label['literal'])

    conn.schemes.update(scheme)
    return jsonify({})


@app.route('/schemes/<string:scheme_id>', methods=['DELETE'])
def scheme_delete(scheme_id):
    conn = get_conn()
    scheme = conn.schemes.get(id=scheme_id)
    conn.schemes.delete(scheme)
    return jsonify({})


@app.route('/schemes/<string:scheme_id>/concepts/', methods=['GET'])
def scheme_concepts(scheme_id):
    conn = get_conn()
    scheme = conn.schemes.get(id=scheme_id)
    concepts = conn.concepts.filter(scheme=scheme)
    return jsonify({
        'concepts': [
            concept.to_python()
            for concept in concepts
        ]
    })
    #return jsonify({'concepts': store.top_concepts(prefix)})


@app.route('/schemes/<string:scheme_id>/concepts/top', methods=['GET'])
def scheme_top_concepts(scheme_id):
    conn = get_conn()
    scheme = conn.schemes.get(id=scheme_id)
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


@app.route('/schemes/<string:scheme_id>/concepts/<string:concept_name>', methods=['DELETE'])
def scheme_concept_delete(scheme_id, concept_name):
    conn = get_conn()
    scheme = conn.schemes.get(id=scheme_id)
    concept = conn.concepts.get(name=concept_name, scheme=scheme)
    conn.concepts.delete(concept)
    return jsonify({})


@app.route('/schemes/<string:scheme_id>/concepts/<string:concept_name>', methods=['PUT'])
def scheme_concept_put(scheme_id, concept_name):

    conn = get_conn()
    scheme = conn.schemes.get(id=scheme_id)
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


@app.route('/schemes/<string:scheme_id>/concepts/<string:concept_name>', methods=['GET'])
def scheme_concept(scheme_id, concept_name):
    conn = get_conn()
    scheme = conn.schemes.get(id=scheme_id)
    concept = conn.concepts.get(name=concept_name, scheme=scheme)

    return jsonify({
        'name': concept.name,
        'relations': [],
        'labels': concept.labels.to_python()
    })


@app.route('/schemes/<string:scheme_id>/concepts/<string:concept_name>/labels/', methods=['PUT'])
def scheme_concept_label(scheme_id, concept_name):
    conn = get_conn()
    data = get_data()
    scheme = conn.schemes.get(id=scheme_id)
    concept = conn.concepts.get_or_create(name=concept_name, scheme=scheme)
    concept.labels.add(data['lang'], data['type'], data['literal'])
    conn.concepts.update(concept)
    return jsonify({})


@app.route('/schemes/<string:scheme_id>/concepts/<string:concept_name>/labels/<string:label_id>', methods=['DELETE'])
def rm_scheme_concept_label(scheme_id, concept_name, label_id):
    conn = get_conn()
    data = get_data()
    scheme = conn.schemes.get(id=scheme_id)
    concept = conn.concepts.get_or_create(name=concept_name, scheme=scheme)
    concept.labels.remove_by_id(label_id)
    conn.concepts.update(concept)
    return jsonify({})



@app.route('/schemes/<string:scheme_id>'
           '/add/relation/<string:relscheme>/<string:relname>'
           '/concept1/<string:scheme1>/<string:concept1>'
           '/concept2/<string:scheme2>/<string:concept2>', methods=['PUT'])
def scheme_add_relation(scheme_id, relscheme, relname,
                        scheme1, concept1, scheme2, concept2):
    store.concept_add_link(scheme_id, relscheme, relname,
                           scheme1, concept1, scheme2, concept2)
    for r1, r2 in SYMMETRIC.items():
        if relname == r1:
            store.concept_add_link(scheme_id, relscheme, r2,
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
