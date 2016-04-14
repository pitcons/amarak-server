# encoding: utf-8
from flask import jsonify, request, g
from protocols.rest import get_conn, get_data
from app import app


@app.route('/schemes/<string:scheme_id>/relations/<string:relation_name>', methods=['PUT'])
def scheme_relation(scheme_id, relation_name):
    # conn = get_conn()
    # data = get_data()
    # scheme = conn.schemes.get(id=scheme_id)
    # relation = conn.relations.

    # for key in ('id', 'name', 'ns_prefix', 'ns_url'):
    #     if key in data:
    #         setattr(scheme, key, data[key])

    return jsonify({})
