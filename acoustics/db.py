from pymongo import MongoClient
from config import config

DB_HOST = config.get('Database', 'host')
DB_PORT = int(config.get('Database', 'port'))

client = MongoClient(DB_HOST, DB_PORT)
db = client.acoustics
songs = db.songs
