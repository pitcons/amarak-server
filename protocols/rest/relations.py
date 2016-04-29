# encoding: utf-8
from flask import jsonify, request, g
from protocols.rest import get_conn, get_data
from amarak.models.relation import Relation
from app import app


@app.route('/schemes/<string:scheme_id>/relations/<string:relation_name>', methods=['PUT'])
def scheme_relation(scheme_id, relation_name):
    conn = get_conn()
    data = get_data()
    scheme = conn.schemes.get(id=scheme_id)

    relation = scheme.relations.get(name=relation_name)
    if not relation:
        scheme.relations.add(Relation(scheme, relation_name))
    else:
        for key in ('name', ):
            if key in data:
                setattr(relation, key, data[key])
        conn.update(relation)

    conn.update(scheme)
    return jsonify({})


@app.route('/schemes/<string:scheme_id>/relations/<string:relation_name>', methods=['DELETE'])
def scheme_relation_delete(scheme_id, relation_name):
    conn = get_conn()
    data = get_data()
    scheme = conn.schemes.get(id=scheme_id)

    relation = scheme.relations.get(name=relation_name)
    if relation:
        scheme.relations.remove(relation)

    conn.update(scheme)
    return jsonify({})
