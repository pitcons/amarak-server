# encoding: utf8
import logging
import sys
from pprint import pprint
import requests

logging.getLogger("requests").setLevel(logging.WARNING)


def fetch_terms(word):
    url = 'http://localhost:8000/rutez/fetch_terms?word={0}'.format(word)
    response = requests.get(url)
    result = response.json()
    return result

def fetch_stairs(word):
    url = 'http://localhost:8000/rutez/fetch_stairs?word={0}'.format(word)
    response = requests.get(url)
    result = response.json()
    return result


if __name__ == '__main__':
    for term, links in fetch_terms(sys.argv[1]).items():
        print term, ":"
        for t1, link, t2 in links:
            print "---> ", t1, '|', link, '|', t2
