from pymongo import MongoClient

client = MongoClient()
db = client.acoustics
songs = db.songs
