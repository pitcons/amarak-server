# encoding: utf-8
import sys
from protocols.export import rdf_export


if __name__ == '__main__':
    result = rdf_export(sys.argv[1], 'rdf')
    print result
