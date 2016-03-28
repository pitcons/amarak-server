import os
import ConfigParser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG = ConfigParser.RawConfigParser()
CONFIG.read(os.path.join(BASE_DIR, 'settings.ini'))
CONFIG.IS_TESTING = False
