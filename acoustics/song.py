import db
from bson.objectid import ObjectId
from os.path import basename, splitext
import re

def get_song(song_id):
    song = db.songs.find_one(ObjectId(song_id))
    song['_id'] = str(song['_id'])
    return song

def urlify(path):
    return 'file://' + path

def pathify(mrl):
    return re.sub(r'^file://', '', mrl)

def add_song(path, title='', artist='', album=''):
    if not title:
        title = splitext(basename(path))[0]
    song = {'title': title, 'artist': artist, 'album': album, 'path': path}
    return str(db.songs.insert(song))
