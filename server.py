# encoding: utf-8
from flask import send_from_directory, redirect
from app import app
from protocols.rest import *

@app.route('/docs/')
def index():
    return redirect('/docs/swagger-ui/index.html?url=/docs/api_ru.yml')

@app.route('/docs/<path:path>')
def send_js(path):
    return send_from_directory('docs', path)

if __name__ == '__main__':
    app.run(port=8000, debug=True, threaded=True)


# import time
# import logging

# from spyne import Application, srpc, ServiceBase, Iterable
# from spyne import UnsignedInteger, String, String
# from spyne.model.primitive import AnyDict
# from spyne.protocol.json import JsonDocument
# from spyne.protocol.http import HttpRpc
# from spyne.protocol.http import HttpPattern
# from spyne.server.wsgi import WsgiApplication

# from store.store import Store

# store = Store()

# class AmarakService(ServiceBase):

#     @srpc(String, String,
#           _patterns=[HttpPattern("/<thesaurus>/fetch_terms")],
#           _returns=AnyDict)
#     def fetch_terms(thesaurus, word):
#         return store.fetch_terms(thesaurus, word.upper().decode('utf-8'))

#     @srpc(String, String,
#           _patterns=[HttpPattern("/<thesaurus>/fetch_stairs")],
#           _returns=AnyDict)
#     def fetch_stairs(thesaurus, word):
#         return store.fetch_stairs(thesaurus, word.upper().decode('utf-8'))

#     @srpc(_returns=AnyDict)
#     def thesauruses():
#         return store.thesauruses()

#     @srpc(String, UnsignedInteger, _returns=String)
#     def put_word(name, times):
#         return


# if __name__=='__main__':
#     # Python daemon boilerplate
#     from wsgiref.simple_server import make_server
#     logging.basicConfig(level=logging.DEBUG)

#     application = Application([AmarakService], 'amarak.http',
#           in_protocol=HttpRpc(validator='soft'),
#           out_protocol=JsonDocument(ignore_wrappers=True),
#       )
#     wsgi_application = WsgiApplication(application)
#     server = make_server('0.0.0.0', 8000, wsgi_application)

#     logging.info("listening to http://127.0.0.1:8000")
#     logging.info("wsdl is at: http://localhost:8000/?wsdl")

#     server.serve_forever()
