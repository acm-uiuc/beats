import db
from timeit import default_timer
from bson.objectid import ObjectId
from os.path import basename, splitext
from os import walk
import re
from mutagen.easyid3 import EasyID3FileType

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
    song = {'title': title, 'artist': artist, 'album': album, 'path': pat}
    return str(db.songs.insert(song))

def remove_songs_in_dir(path):
    db.songs.remove({'path': {'$regex':'^%s.*' % path}})

def add_songs_in_dir(path, required={"title", "artist", "album"}):
    remove_songs_in_dir(path)
    start = default_timer()
    metadata = EasyID3FileType()
    songs = []
    filepath = ""
    for root, dirs, files in walk(path):
        for mp3 in files:
            if splitext(mp3)[1] == ".mp3":
                filepath = root + "/" + mp3
                metadata.load(filepath)
                for tag in required:
                    try:
                        values = metadata[tag]
                    except:
                        values = ""
                        metadata[tag] = values
                #metadata.load(mp3)
                if not metadata["title"]:
                    title = splitext(basename(path))[0]
                songs.append({'title': metadata['title'], 
                    'artist': metadata['artist'],
                    'album': metadata['album'],
                    'path': filepath})
    db.songs.insert(songs)   
    print default_timer() - start
