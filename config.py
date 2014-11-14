import ConfigParser
import os

config = ConfigParser.RawConfigParser()
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'beats.cfg'))
