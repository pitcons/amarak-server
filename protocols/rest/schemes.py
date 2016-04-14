# encoding: utf-8
from flask import jsonify, request, g
from protocols.rest import get_conn, get_data
from amarak.models.relation import Relation
from app import app


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
            "relations": scheme.relations.to_python(),
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

    if 'relations' in data:
        scheme.relations.clear()
        for relation in data['relations']:
            if relation['scheme'] == scheme.id:
                scheme.relations.add(Relation(scheme, relation['name']))

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
